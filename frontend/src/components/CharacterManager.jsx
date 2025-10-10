import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/config';
import { toast } from 'sonner';
import { Users, Plus, Edit, Trash2, Image as ImageIcon, Sparkles, X, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';

const CharacterManager = ({ activeProject }) => {
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    reference_images: [],
    lora: '',
    trigger_words: '',
    style_notes: ''
  });
  const [imageUrls, setImageUrls] = useState(''); // Comma-separated URLs

  useEffect(() => {
    if (activeProject) {
      fetchCharacters();
    }
  }, [activeProject]);

  const fetchCharacters = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/characters`, {
        params: { project_id: activeProject.id }
      });
      setCharacters(response.data);
    } catch (error) {
      console.error('Error fetching characters:', error);
      toast.error('Failed to load characters');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCharacter = () => {
    setIsEditing(false);
    setFormData({
      name: '',
      description: '',
      reference_images: [],
      lora: '',
      trigger_words: '',
      style_notes: ''
    });
    setImageUrls('');
    setIsDialogOpen(true);
  };

  const handleEditCharacter = (character) => {
    setIsEditing(true);
    setSelectedCharacter(character);
    setFormData({
      name: character.name,
      description: character.description || '',
      reference_images: character.reference_images || [],
      lora: character.lora || '',
      trigger_words: character.trigger_words || '',
      style_notes: character.style_notes || ''
    });
    setImageUrls((character.reference_images || []).join(', '));
    setIsDialogOpen(true);
  };

  const handleSaveCharacter = async () => {
    if (!formData.name.trim()) {
      toast.error('Character name is required');
      return;
    }

    try {
      // Parse image URLs from comma-separated string
      const reference_images = imageUrls
        .split(',')
        .map(url => url.trim())
        .filter(url => url.length > 0);

      const characterData = {
        ...formData,
        reference_images,
        project_id: activeProject.id
      };

      if (isEditing && selectedCharacter) {
        // Update existing character
        await axios.put(`${API}/characters/${selectedCharacter.id}`, characterData);
        toast.success('Character updated successfully');
      } else {
        // Create new character
        await axios.post(`${API}/characters`, characterData);
        toast.success('Character created successfully');
      }

      setIsDialogOpen(false);
      fetchCharacters();
    } catch (error) {
      console.error('Error saving character:', error);
      toast.error(`Failed to ${isEditing ? 'update' : 'create'} character`);
    }
  };

  const handleDeleteCharacter = async (characterId) => {
    if (!window.confirm('Are you sure you want to delete this character?')) {
      return;
    }

    try {
      await axios.delete(`${API}/characters/${characterId}`);
      toast.success('Character deleted successfully');
      fetchCharacters();
    } catch (error) {
      console.error('Error deleting character:', error);
      toast.error('Failed to delete character');
    }
  };

  const handleViewCharacter = (character) => {
    setSelectedCharacter(character);
    setFormData({
      name: character.name,
      description: character.description || '',
      reference_images: character.reference_images || [],
      lora: character.lora || '',
      trigger_words: character.trigger_words || '',
      style_notes: character.style_notes || ''
    });
    setImageUrls((character.reference_images || []).join(', '));
  };

  if (!activeProject) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Users className="w-16 h-16 text-secondary mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-primary mb-2">No Project Selected</h3>
          <p className="text-sm text-secondary">
            Select a project to manage characters
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="border-b border-panel p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-primary flex items-center gap-2">
              <Users className="w-6 h-6" />
              Character Manager
            </h2>
            <p className="text-sm text-secondary mt-1">
              Create and manage characters for consistent generation
            </p>
          </div>
          <Button onClick={handleCreateCharacter} className="gap-2">
            <Plus className="w-4 h-4" />
            New Character
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-secondary">Loading characters...</div>
          </div>
        ) : characters.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md">
              <Users className="w-16 h-16 text-secondary mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-primary mb-2">No Characters Yet</h3>
              <p className="text-sm text-secondary mb-4">
                Create characters to maintain consistency across your project.
                Characters can include reference images, LoRAs, and style notes.
              </p>
              <Button onClick={handleCreateCharacter} className="gap-2">
                <Plus className="w-4 h-4" />
                Create First Character
              </Button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {characters.map((character) => (
              <Card key={character.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg">{character.name}</CardTitle>
                      <CardDescription className="mt-1 line-clamp-2">
                        {character.description || 'No description'}
                      </CardDescription>
                    </div>
                    <div className="flex gap-1 ml-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEditCharacter(character)}
                        className="h-8 w-8 p-0"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteCharacter(character.id)}
                        className="h-8 w-8 p-0 text-red-500 hover:text-red-600"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {/* Reference Images */}
                  {character.reference_images && character.reference_images.length > 0 && (
                    <div>
                      <Label className="text-xs text-secondary mb-1 block">Reference Images</Label>
                      <div className="flex gap-2 flex-wrap">
                        {character.reference_images.slice(0, 3).map((img, idx) => (
                          <div
                            key={idx}
                            className="w-16 h-16 rounded border border-panel bg-panel-dark flex items-center justify-center overflow-hidden"
                          >
                            <img
                              src={img}
                              alt={`${character.name} reference ${idx + 1}`}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.parentElement.innerHTML = '<ImageIcon class="w-6 h-6 text-secondary" />';
                              }}
                            />
                          </div>
                        ))}
                        {character.reference_images.length > 3 && (
                          <div className="w-16 h-16 rounded border border-panel bg-panel-dark flex items-center justify-center">
                            <span className="text-xs text-secondary">
                              +{character.reference_images.length - 3}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* LoRA */}
                  {character.lora && (
                    <div>
                      <Label className="text-xs text-secondary mb-1 block">LoRA</Label>
                      <Badge variant="secondary" className="text-xs">
                        {character.lora}
                      </Badge>
                    </div>
                  )}

                  {/* Trigger Words */}
                  {character.trigger_words && (
                    <div>
                      <Label className="text-xs text-secondary mb-1 block">Trigger Words</Label>
                      <p className="text-sm text-primary truncate">{character.trigger_words}</p>
                    </div>
                  )}

                  {/* Style Notes */}
                  {character.style_notes && (
                    <div>
                      <Label className="text-xs text-secondary mb-1 block">Style Notes</Label>
                      <p className="text-xs text-secondary line-clamp-2">{character.style_notes}</p>
                    </div>
                  )}

                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full mt-2 gap-2"
                    onClick={() => handleViewCharacter(character)}
                  >
                    <Sparkles className="w-4 h-4" />
                    View Details
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Create/Edit Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {isEditing ? 'Edit Character' : 'Create New Character'}
            </DialogTitle>
            <DialogDescription>
              Define character details for consistent generation across your project
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Character Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Sarah the Adventurer"
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe the character's appearance, personality, etc."
                rows={3}
              />
            </div>

            {/* Reference Images */}
            <div className="space-y-2">
              <Label htmlFor="images">Reference Image URLs</Label>
              <Textarea
                id="images"
                value={imageUrls}
                onChange={(e) => setImageUrls(e.target.value)}
                placeholder="Enter image URLs separated by commas"
                rows={2}
              />
              <p className="text-xs text-secondary">
                Comma-separated URLs to reference images
              </p>
            </div>

            {/* LoRA */}
            <div className="space-y-2">
              <Label htmlFor="lora">LoRA Model</Label>
              <Input
                id="lora"
                value={formData.lora}
                onChange={(e) => setFormData({ ...formData, lora: e.target.value })}
                placeholder="e.g., character_lora_v1.safetensors"
              />
              <p className="text-xs text-secondary">
                Specific LoRA model for this character
              </p>
            </div>

            {/* Trigger Words */}
            <div className="space-y-2">
              <Label htmlFor="trigger">Trigger Words</Label>
              <Input
                id="trigger"
                value={formData.trigger_words}
                onChange={(e) => setFormData({ ...formData, trigger_words: e.target.value })}
                placeholder="e.g., sarah_adv, brown_hair, green_eyes"
              />
              <p className="text-xs text-secondary">
                Keywords to activate character in prompts
              </p>
            </div>

            {/* Style Notes */}
            <div className="space-y-2">
              <Label htmlFor="style">Style Notes</Label>
              <Textarea
                id="style"
                value={formData.style_notes}
                onChange={(e) => setFormData({ ...formData, style_notes: e.target.value })}
                placeholder="Additional style guidance for consistent generation"
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveCharacter}>
              {isEditing ? 'Update' : 'Create'} Character
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CharacterManager;
