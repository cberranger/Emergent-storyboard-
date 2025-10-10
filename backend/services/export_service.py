"""Export service for timeline data to various formats"""
from typing import List, Dict, Any
from datetime import datetime
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import logging

logger = logging.getLogger(__name__)


class ExportService:
    """Handles export of timeline data to various professional formats"""

    @staticmethod
    async def export_final_cut_pro(db, project_id: str) -> str:
        """
        Export timeline to Final Cut Pro XML format

        Args:
            db: Database instance
            project_id: Project ID

        Returns:
            XML string in FCPXML format
        """
        # Get project
        project_data = await db.projects.find_one({"id": project_id})
        if not project_data:
            raise ValueError("Project not found")

        # Get all scenes and clips
        scenes = await db.scenes.find({"project_id": project_id}).sort("order").to_list(100)

        # Create FCPXML root
        fcpxml = ET.Element('fcpxml', version='1.9')
        resources = ET.SubElement(fcpxml, 'resources')
        library = ET.SubElement(fcpxml, 'library')
        event = ET.SubElement(library, 'event', name=project_data['name'])
        project_elem = ET.SubElement(event, 'project', name=project_data['name'])
        sequence = ET.SubElement(project_elem, 'sequence', {
            'format': 'r1',
            'duration': f"{project_data.get('music_duration', 0)}s"
        })
        spine = ET.SubElement(sequence, 'spine')

        # Add clips to spine
        for scene in scenes:
            clips = await db.clips.find({"scene_id": scene['id']}).sort("timeline_position").to_list(100)

            for clip in clips:
                # Get selected content
                selected_video_id = clip.get('selected_video_id')
                selected_video = None

                if selected_video_id:
                    for video in clip.get('generated_videos', []):
                        if video['id'] == selected_video_id:
                            selected_video = video
                            break

                if selected_video:
                    clip_elem = ET.SubElement(spine, 'video', {
                        'name': clip['name'],
                        'offset': f"{clip['timeline_position']}s",
                        'duration': f"{clip['length']}s",
                        'ref': f"r{len(resources)}"
                    })

                    # Add resource
                    asset = ET.SubElement(resources, 'asset', {
                        'id': f"r{len(resources)}",
                        'name': clip['name'],
                        'src': selected_video['url'],
                        'duration': f"{clip['length']}s"
                    })

        # Convert to pretty XML string
        rough_string = ET.tostring(fcpxml, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    @staticmethod
    async def export_premiere_edl(db, project_id: str) -> str:
        """
        Export timeline to Adobe Premiere EDL format

        Args:
            db: Database instance
            project_id: Project ID

        Returns:
            EDL string
        """
        # Get project
        project_data = await db.projects.find_one({"id": project_id})
        if not project_data:
            raise ValueError("Project not found")

        # Get all scenes and clips
        scenes = await db.scenes.find({"project_id": project_id}).sort("order").to_list(100)

        # Build EDL
        edl_lines = [
            f"TITLE: {project_data['name']}",
            f"FCM: NON-DROP FRAME",
            "",
        ]

        clip_number = 1
        for scene in scenes:
            clips = await db.clips.find({"scene_id": scene['id']}).sort("timeline_position").to_list(100)

            for clip in clips:
                # Get selected content
                selected_video_id = clip.get('selected_video_id')
                if not selected_video_id:
                    continue

                selected_video = None
                for video in clip.get('generated_videos', []):
                    if video['id'] == selected_video_id:
                        selected_video = video
                        break

                if selected_video:
                    start_tc = ExportService._seconds_to_timecode(clip['timeline_position'])
                    end_tc = ExportService._seconds_to_timecode(clip['timeline_position'] + clip['length'])

                    edl_lines.extend([
                        f"{clip_number:03d}  {clip['name']} V     C        {start_tc} {end_tc} {start_tc} {end_tc}",
                        f"* FROM CLIP NAME: {clip['name']}",
                        f"* SOURCE FILE: {selected_video['url']}",
                        ""
                    ])
                    clip_number += 1

        return "\n".join(edl_lines)

    @staticmethod
    async def export_davinci_resolve(db, project_id: str) -> str:
        """
        Export timeline to DaVinci Resolve AAF-compatible format

        Args:
            db: Database instance
            project_id: Project ID

        Returns:
            XML string compatible with DaVinci Resolve
        """
        # Get project
        project_data = await db.projects.find({"id": project_id})
        if not project_data:
            raise ValueError("Project not found")

        # For DaVinci Resolve, we'll use a simplified XML format
        # In production, you'd want to use proper AAF library
        root = ET.Element('resolve_timeline', name=project_data['name'])
        tracks = ET.SubElement(root, 'tracks')
        video_track = ET.SubElement(tracks, 'track', type='video', number='1')

        # Get all scenes and clips
        scenes = await db.scenes.find({"project_id": project_id}).sort("order").to_list(100)

        for scene in scenes:
            clips = await db.clips.find({"scene_id": scene['id']}).sort("timeline_position").to_list(100)

            for clip in clips:
                selected_video_id = clip.get('selected_video_id')
                if not selected_video_id:
                    continue

                selected_video = None
                for video in clip.get('generated_videos', []):
                    if video['id'] == selected_video_id:
                        selected_video = video
                        break

                if selected_video:
                    clip_elem = ET.SubElement(video_track, 'clip', {
                        'name': clip['name'],
                        'start': str(clip['timeline_position']),
                        'duration': str(clip['length']),
                        'source': selected_video['url']
                    })

                    # Add metadata
                    metadata = ET.SubElement(clip_elem, 'metadata')
                    ET.SubElement(metadata, 'prompt').text = selected_video.get('prompt', '')
                    ET.SubElement(metadata, 'model').text = selected_video.get('model_name', '')

        # Convert to pretty XML
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    @staticmethod
    async def export_json(db, project_id: str) -> Dict[str, Any]:
        """
        Export complete project data to JSON

        Args:
            db: Database instance
            project_id: Project ID

        Returns:
            Dictionary with complete project data
        """
        import json

        # Get project
        project_data = await db.projects.find_one({"id": project_id})
        if not project_data:
            raise ValueError("Project not found")

        # Get all scenes
        scenes = await db.scenes.find({"project_id": project_id}).sort("order").to_list(100)

        # Get all clips for each scene
        for scene in scenes:
            clips = await db.clips.find({"scene_id": scene['id']}).sort("timeline_position").to_list(100)
            scene['clips'] = clips

        # Build export data
        export_data = {
            "format": "storycanvas_v1",
            "exported_at": datetime.utcnow().isoformat(),
            "project": project_data,
            "scenes": scenes
        }

        # Convert datetime objects to strings
        def serialize_dates(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        return json.loads(json.dumps(export_data, default=serialize_dates))

    @staticmethod
    def _seconds_to_timecode(seconds: float, fps: int = 30) -> str:
        """Convert seconds to timecode format HH:MM:SS:FF"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        frames = int((seconds % 1) * fps)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"


# Global instance
export_service = ExportService()
