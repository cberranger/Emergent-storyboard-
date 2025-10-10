import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DEFAULT_HOTKEYS, formatHotkey } from '@/hooks/useHotkeys';

const HotkeyHelpDialog = ({ open, onOpenChange }) => {
  // Group hotkeys by category
  const hotkeyGroups = {
    'Playback': [' ', 'k', 'j', 'l', '0', 'home', 'end'],
    'Navigation': ['arrowleft', 'arrowright', 'arrowup', 'arrowdown'],
    'Creation': ['n', 'ctrl+n', 'ctrl+s', 'g', 'ctrl+g'],
    'Editing': ['delete', 'backspace', 'ctrl+z', 'ctrl+y', 'ctrl+shift+z', 'ctrl+c', 'ctrl+v', 'ctrl+x', 'ctrl+d'],
    'View': ['f', 'tab', 'ctrl+1', 'ctrl+2', 'ctrl+3'],
    'Selection': ['ctrl+a', 'escape'],
    'Zoom': ['ctrl+=', 'ctrl+-', 'ctrl+0'],
    'Help': ['?', 'ctrl+/'],
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Keyboard Shortcuts</DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          {Object.entries(hotkeyGroups).map(([category, keys]) => (
            <Card key={category}>
              <CardHeader>
                <CardTitle className="text-lg">{category}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {keys.map(key => (
                    <div key={key} className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">
                        {DEFAULT_HOTKEYS[key]}
                      </span>
                      <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded-lg dark:bg-gray-600 dark:text-gray-100 dark:border-gray-500">
                        {formatHotkey(key)}
                      </kbd>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <p className="text-sm text-blue-900 dark:text-blue-100">
            <strong>Tip:</strong> Press <kbd className="px-2 py-1 text-xs font-semibold bg-white dark:bg-gray-700 border rounded">?</kbd> or{' '}
            <kbd className="px-2 py-1 text-xs font-semibold bg-white dark:bg-gray-700 border rounded">Ctrl+/</kbd>{' '}
            to toggle this help dialog anytime.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default HotkeyHelpDialog;
