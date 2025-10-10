import { useEffect, useCallback } from 'react';

/**
 * Custom hook for handling keyboard shortcuts
 * @param {Object} keyMap - Map of keys to handler functions
 * @param {Array} dependencies - Dependencies for useCallback
 * @param {boolean} enabled - Whether hotkeys are enabled (default: true)
 */
export const useHotkeys = (keyMap, dependencies = [], enabled = true) => {
  const handleKeyDown = useCallback(
    (event) => {
      if (!enabled) return;

      // Don't trigger hotkeys when typing in input fields
      const target = event.target;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.contentEditable === 'true'
      ) {
        return;
      }

      // Build key combination string
      const modifiers = [];
      if (event.ctrlKey || event.metaKey) modifiers.push('ctrl');
      if (event.altKey) modifiers.push('alt');
      if (event.shiftKey) modifiers.push('shift');

      const key = event.key.toLowerCase();
      const combo = modifiers.length > 0 ? `${modifiers.join('+')}+${key}` : key;

      // Check if handler exists for this combination
      if (keyMap[combo]) {
        event.preventDefault();
        keyMap[combo](event);
      }
    },
    [keyMap, enabled, ...dependencies]
  );

  useEffect(() => {
    if (enabled) {
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [handleKeyDown, enabled]);
};

/**
 * Default hotkey mappings for the application
 */
export const DEFAULT_HOTKEYS = {
  // Playback
  ' ': 'Toggle play/pause',
  'k': 'Toggle play/pause (alternative)',
  'j': 'Rewind',
  'l': 'Fast forward',
  '0': 'Go to start',
  'home': 'Go to start',
  'end': 'Go to end',

  // Navigation
  'arrowleft': 'Previous clip',
  'arrowright': 'Next clip',
  'arrowup': 'Scroll up',
  'arrowdown': 'Scroll down',

  // Creation
  'n': 'New clip',
  'ctrl+n': 'New project',
  'ctrl+s': 'Save',
  'g': 'Generate content',
  'ctrl+g': 'Batch generate',

  // Editing
  'delete': 'Delete selected',
  'backspace': 'Delete selected',
  'ctrl+z': 'Undo',
  'ctrl+y': 'Redo',
  'ctrl+shift+z': 'Redo (alternative)',
  'ctrl+c': 'Copy',
  'ctrl+v': 'Paste',
  'ctrl+x': 'Cut',
  'ctrl+d': 'Duplicate',

  // View
  'f': 'Toggle fullscreen',
  'tab': 'Toggle sidebar',
  'ctrl+1': 'Switch to timeline view',
  'ctrl+2': 'Switch to scenes view',
  'ctrl+3': 'Switch to servers view',

  // Selection
  'ctrl+a': 'Select all',
  'escape': 'Deselect / Close dialog',

  // Zoom
  'ctrl+=': 'Zoom in',
  'ctrl+-': 'Zoom out',
  'ctrl+0': 'Reset zoom',

  // Help
  '?': 'Show hotkey help',
  'ctrl+/': 'Show hotkey help',
};

/**
 * Format hotkey string for display
 * @param {string} hotkey - Raw hotkey string
 * @returns {string} - Formatted hotkey for display
 */
export const formatHotkey = (hotkey) => {
  return hotkey
    .split('+')
    .map(key => {
      // Capitalize and format special keys
      const formatted = {
        'ctrl': '⌃',
        'alt': '⌥',
        'shift': '⇧',
        'meta': '⌘',
        'arrowleft': '←',
        'arrowright': '→',
        'arrowup': '↑',
        'arrowdown': '↓',
        'enter': '↵',
        'escape': 'Esc',
        'backspace': '⌫',
        'delete': 'Del',
        ' ': 'Space',
      };

      return formatted[key.toLowerCase()] || key.toUpperCase();
    })
    .join(' ');
};
