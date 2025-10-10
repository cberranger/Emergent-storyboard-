from typing import List, Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TimelineValidator:
    """Validates timeline positions and checks for overlaps"""

    @staticmethod
    def check_overlap(
        clip_id: str,
        new_position: float,
        clip_length: float,
        other_clips: List[Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if clip at new position would overlap with other clips

        Args:
            clip_id: ID of the clip being moved
            new_position: Proposed new position in seconds
            clip_length: Length of the clip in seconds
            other_clips: List of other Clip objects in the scene

        Returns:
            (is_valid, error_message)
        """
        new_end = new_position + clip_length

        for other_clip in other_clips:
            # Skip self
            if other_clip.id == clip_id:
                continue

            other_start = other_clip.timeline_position
            other_end = other_clip.timeline_position + other_clip.length

            # Check for overlap
            # Overlap occurs if: new_start < other_end AND new_end > other_start
            if new_position < other_end and new_end > other_start:
                overlap_amount = min(new_end, other_end) - max(new_position, other_start)
                return False, (
                    f"Clip would overlap with '{other_clip.name}' by {overlap_amount:.2f} seconds. "
                    f"Other clip occupies {other_start:.2f}s to {other_end:.2f}s"
                )

        return True, None

    @staticmethod
    def find_next_available_position(
        clip_length: float,
        other_clips: List[Any],
        preferred_position: float = 0
    ) -> float:
        """
        Find the next available position on timeline

        Args:
            clip_length: Length of the clip to place
            other_clips: List of existing clips
            preferred_position: Starting position to search from

        Returns:
            Next available position in seconds
        """
        # Sort clips by position
        sorted_clips = sorted(other_clips, key=lambda c: c.timeline_position)

        # Try preferred position first
        current_pos = preferred_position

        for clip in sorted_clips:
            clip_start = clip.timeline_position
            clip_end = clip.timeline_position + clip.length

            # If current position would overlap, move to after this clip
            if current_pos < clip_end and (current_pos + clip_length) > clip_start:
                current_pos = clip_end + 0.1  # Add small gap

        return round(current_pos, 2)

    @staticmethod
    def get_timeline_summary(clips: List[Any]) -> Dict[str, Any]:
        """
        Get summary of timeline usage

        Args:
            clips: List of Clip objects

        Returns:
            Dictionary with timeline statistics
        """
        if not clips:
            return {
                "total_clips": 0,
                "total_duration": 0,
                "timeline_end": 0,
                "gaps": []
            }

        sorted_clips = sorted(clips, key=lambda c: c.timeline_position)
        total_duration = sum(c.length for c in clips)
        timeline_end = max(c.timeline_position + c.length for c in clips)

        # Find gaps
        gaps = []
        for i in range(len(sorted_clips) - 1):
            current_end = sorted_clips[i].timeline_position + sorted_clips[i].length
            next_start = sorted_clips[i + 1].timeline_position

            if next_start > current_end:
                gaps.append({
                    "start": current_end,
                    "end": next_start,
                    "duration": next_start - current_end
                })

        return {
            "total_clips": len(clips),
            "total_duration": round(total_duration, 2),
            "timeline_end": round(timeline_end, 2),
            "gaps": gaps
        }


timeline_validator = TimelineValidator()
