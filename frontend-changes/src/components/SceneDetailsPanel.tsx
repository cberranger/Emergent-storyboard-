import { GenerationPanel } from './GenerationPanel';
import { SceneEditor } from './SceneEditor';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from './ui/sheet';

interface SceneDetailsPanelProps {
  scene: any;
  clip: any;
  onClose: () => void;
}

export function SceneDetailsPanel({ scene, clip, onClose }: SceneDetailsPanelProps) {
  const isOpen = !!(scene || clip);

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent 
        side="right" 
        className="w-full sm:max-w-2xl bg-neutral-900 border-neutral-800 overflow-y-auto"
      >
        <SheetHeader>
          <SheetTitle>
            {clip ? 'Clip Editor' : scene ? 'Scene Editor' : ''}
          </SheetTitle>
        </SheetHeader>

        {clip && <GenerationPanel clip={clip} />}
        {scene && !clip && <SceneEditor scene={scene} />}
      </SheetContent>
    </Sheet>
  );
}
