import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/config';
import { toast } from 'sonner';
import {
  Wand2, Sparkles, Clock, AlertCircle, CheckCircle, 
  RefreshCw, Download, Eye, Settings, User, Calendar,
  Zap, Image as ImageIcon, Layers, Play
} from 'lucide-react';
import { Button } from '@/components/ui/button';
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';

const FaceFusionProcessor = ({ character, onProcessComplete }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [facefusionStatus, setFacefusionStatus] = useState('offline');
  const [selectedImage, setSelectedImage] = useState('');
  const [processingResults, setProcessingResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [facefusionUrl, setFacefusionUrl] = useState('http://localhost:7870');
  const [targetAge, setTargetAge] = useState(25);

  const enhancementModels = [
    { value: 'gfpgan_1.4', label: 'GFPGAN 1.4', description: 'General purpose face restoration' },
    { value: 'codeformer', label: 'CodeFormer', description: 'High-quality face restoration' },
    { value: 'restoreformer_plus_plus', label: 'RestoreFormer++', description: 'Advanced face restoration' }
  ];

  const processingOperations = [
    {
      id: 'enhance',
      name: 'Face Enhancement',
      description: 'Improve face quality and clarity',
      icon: Sparkles,
      color: 'blue'
    },
    {
      id: 'age_adjust',
      name: 'Age Adjustment',
      description: 'Modify character age appearance',
      icon: Calendar,
      color: 'green'
    },
    {
      id: 'swap',
      name: 'Face Swap',
      description: 'Replace face with character face',
      icon: User,
      color: 'purple'
    }
  ];

  useEffect(() => {
    if (isOpen) {
      checkFaceFusionStatus();
    }
  }, [isOpen]);

  const checkFaceFusionStatus = async () => {
    try {
      const response = await axios.get(`${API}/facefusion/status`, {
        params: { facefusion_url: facefusionUrl }
      });
      setFacefusionStatus(response.data.is_online ? 'online' : 'offline');
    } catch (error) {
      setFacefusionStatus('offline');
      console.error('Error checking FaceFusion status:', error);
    }
  };

  const enhanceFace = async (imageUrl, model = 'gfpgan_1.4') => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/facefusion/enhance-face`, {
        character_id: character.id,
        image_url: imageUrl,
        enhancement_model: model,
        facefusion_url: facefusionUrl
      });

      return {
        success: true,
        result: response.data,
        type: 'enhance',
        original: imageUrl,
        processed: response.data.enhanced_image,
        model: model
      };
    } catch (error) {
      console.error('Error enhancing face:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Face enhancement failed',
        type: 'enhance'
      };
    } finally {
      setLoading(false);
    }
  };

  const adjustFaceAge = async (imageUrl, targetAge) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/facefusion/adjust-face-age`, {
        character_id: character.id,
        image_url: imageUrl,
        target_age: targetAge,
        facefusion_url: facefusionUrl
      });

      return {
        success: true,
        result: response.data,
        type: 'age_adjust',
        original: imageUrl,
        processed: response.data.adjusted_image,
        targetAge: targetAge
      };
    } catch (error) {
      console.error('Error adjusting face age:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Age adjustment failed',
        type: 'age_adjust'
      };
    } finally {
      setLoading(false);
    }
  };

  const swapFace = async (sourceFaceUrl, targetImageUrl) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/facefusion/swap-face`, {
        character_id: character.id,
        source_face_url: sourceFaceUrl,
        target_image_url: targetImageUrl,
        facefusion_url: facefusionUrl
      });

      return {
        success: true,
        result: response.data,
        type: 'swap',
        original: targetImageUrl,
        processed: response.data.swapped_image,
        sourceFace: sourceFaceUrl
      };
    } catch (error) {
      console.error('Error swapping face:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Face swap failed',
        type: 'swap'
      };
    } finally {
      setLoading(false);
    }
  };

  const batchProcess = async (operations) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/facefusion/batch-process`, {
        character_id: character.id,
        operations: operations,
        facefusion_url: facefusionUrl
      });

      return {
        success: true,
        results: response.data.results,
        summary: {
          total: response.data.total_operations,
          successful: response.data.successful_operations
        }
      };
    } catch (error) {
      console.error('Error batch processing:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Batch processing failed'
      };
    } finally {
      setLoading(false);
    }
  };

  const handleEnhance = async (model) => {
    if (!selectedImage) {
      toast.error('Please select an image to enhance');
      return;
    }

    const result = await enhanceFace(selectedImage, model);
    setProcessingResults(prev => [...prev, result]);
    
    if (result.success) {
      toast.success('Face enhanced successfully');
      if (onProcessComplete) {
        onProcessComplete(result.processed);
      }
    } else {
      toast.error(result.error);
    }
  };

  const handleAgeAdjust = async (targetAge) => {
    if (!selectedImage) {
      toast.error('Please select an image to adjust');
      return;
    }

    const result = await adjustFaceAge(selectedImage, targetAge);
    setProcessingResults(prev => [...prev, result]);
    
    if (result.success) {
      toast.success(`Face age adjusted to ${targetAge} years`);
      if (onProcessComplete) {
        onProcessComplete(result.processed);
      }
    } else {
      toast.error(result.error);
    }
  };

  const handleBatchProcess = async () => {
    const operations = [];
    
    // Add enhancement operation if image selected
    if (selectedImage) {
      operations.push({
        type: 'enhance',
        image_url: selectedImage,
        enhancement_model: 'gfpgan_1.4'
      });
    }

    if (operations.length === 0) {
      toast.error('Please select an image to process');
      return;
    }

    const result = await batchProcess(operations);
    
    if (result.success) {
      toast.success(`Batch processed ${result.summary.successful}/${result.summary.total} operations`);
      setProcessingResults(prev => [...prev, ...result.results]);
      
      if (onProcessComplete) {
        result.results.forEach(r => {
          if (r.success && onProcessComplete) {
            onProcessComplete(r.result_url);
          }
        });
      }
    } else {
      toast.error(result.error);
    }
  };

  const getImageOptions = () => {
    const images = [];
    
    if (character.face_image) {
      images.push({ url: character.face_image, label: 'Face Image', type: 'face' });
    }
    
    if (character.reference_images && character.reference_images.length > 0) {
      character.reference_images.forEach((img, idx) => {
        images.push({ url: img, label: `Reference ${idx + 1}`, type: 'reference' });
      });
    }
    
    return images;
  };

  const imageOptions = getImageOptions();

  return (
    <>
      <Button 
        onClick={() => setIsOpen(true)} 
        variant="outline" 
        className="gap-2"
        disabled={facefusionStatus === 'offline'}
      >
        <Wand2 className="w-4 h-4" />
        FaceFusion
        {facefusionStatus === 'offline' && (
          <Badge variant="secondary" className="text-xs">Offline</Badge>
        )}
      </Button>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Wand2 className="w-5 h-5" />
              FaceFusion Character Processor
            </DialogTitle>
            <DialogDescription>
              Advanced face enhancement and manipulation for {character.name}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Status Check */}
            <Card className={facefusionStatus === 'online' ? 'border-green-500' : 'border-red-500'}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2">
                    {facefusionStatus === 'online' ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-500" />
                    )}
                    FaceFusion Server Status
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={checkFaceFusionStatus}
                    disabled={loading}
                  >
                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    Check
                  </Button>
                </div>
                <CardDescription>
                  {facefusionStatus === 'online' 
                    ? 'FaceFusion server is online and ready to process'
                    : 'FaceFusion server is not accessible. Please check if FaceFusion is running.'
                  }
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <Label>Server URL:</Label>
                  <Input
                    value={facefusionUrl}
                    onChange={(e) => setFacefusionUrl(e.target.value)}
                    placeholder="http://localhost:7870"
                    className="flex-1"
                  />
                </div>
              </CardContent>
            </Card>

            {facefusionStatus === 'online' && (
              <Tabs defaultValue="enhance" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="enhance">Enhance</TabsTrigger>
                  <TabsTrigger value="adjust">Adjust Age</TabsTrigger>
                  <TabsTrigger value="batch">Batch Process</TabsTrigger>
                </TabsList>

                {/* Image Selection */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Select Image</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {imageOptions.map((img, idx) => (
                        <div
                          key={idx}
                          className={`cursor-pointer rounded-lg border-2 p-2 transition-all ${
                            selectedImage === img.url
                              ? 'border-primary bg-primary/10'
                              : 'border-panel hover:border-primary/50'
                          }`}
                          onClick={() => setSelectedImage(img.url)}
                        >
                          <div className="aspect-square rounded overflow-hidden mb-2">
                            <img
                              src={img.url}
                              alt={img.label}
                              className="w-full h-full object-cover"
                            />
                          </div>
                          <p className="text-sm font-medium">{img.label}</p>
                          <Badge variant="outline" className="text-xs mt-1">
                            {img.type}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <TabsContent value="enhance" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Sparkles className="w-5 h-5" />
                        Face Enhancement
                      </CardTitle>
                      <CardDescription>
                        Improve face quality, clarity, and detail using advanced AI models
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <Label>Enhancement Model</Label>
                        <Select defaultValue="gfpgan_1.4">
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {enhancementModels.map((model) => (
                              <SelectItem key={model.value} value={model.value}>
                                <div>
                                  <div className="font-medium">{model.label}</div>
                                  <div className="text-sm text-secondary">{model.description}</div>
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <Button 
                        onClick={() => handleEnhance('gfpgan_1.4')}
                        disabled={loading || !selectedImage}
                        className="w-full"
                      >
                        <Sparkles className="w-4 h-4 mr-2" />
                        {loading ? 'Enhancing...' : 'Enhance Face'}
                      </Button>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="adjust" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Calendar className="w-5 h-5" />
                        Age Adjustment
                      </CardTitle>
                      <CardDescription>
                        Modify character appearance to target age (0-100 years)
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <Label>Target Age: {targetAge} years</Label>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          value={targetAge}
                          onChange={(e) => {
                            const value = parseInt(e.target.value);
                            setTargetAge(value);
                          }}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-secondary">
                          <span>0</span>
                          <span>25</span>
                          <span>50</span>
                          <span>75</span>
                          <span>100</span>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-2">
                        <Button 
                          onClick={() => handleAgeAdjust(20)}
                          disabled={loading || !selectedImage}
                          variant="outline"
                        >
                          Younger (20)
                        </Button>
                        <Button 
                          onClick={() => handleAgeAdjust(40)}
                          disabled={loading || !selectedImage}
                          variant="outline"
                        >
                          Mature (40)
                        </Button>
                        <Button 
                          onClick={() => handleAgeAdjust(60)}
                          disabled={loading || !selectedImage}
                          variant="outline"
                        >
                          Older (60)
                        </Button>
                        <Button 
                          onClick={() => handleAgeAdjust(targetAge)}
                          disabled={loading || !selectedImage}
                        >
                          Apply ({targetAge})
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="batch" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Layers className="w-5 h-5" />
                        Batch Processing
                      </CardTitle>
                      <CardDescription>
                        Process multiple operations on selected images automatically
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-3">
                        {processingOperations.map((op) => (
                          <div key={op.id} className="flex items-center gap-3 p-3 rounded-lg border">
                            <op.icon className={`w-5 h-5 text-${op.color}-500`} />
                            <div className="flex-1">
                              <div className="font-medium">{op.name}</div>
                              <div className="text-sm text-secondary">{op.description}</div>
                            </div>
                            <Badge variant="outline" className="capitalize">
                              {op.type}
                            </Badge>
                          </div>
                        ))}
                      </div>
                      
                      <Button 
                        onClick={handleBatchProcess}
                        disabled={loading || !selectedImage}
                        className="w-full"
                      >
                        <Play className="w-4 h-4 mr-2" />
                        {loading ? 'Processing...' : 'Start Batch Processing'}
                      </Button>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            )}
          </div>

          {/* Processing Results */}
          {processingResults.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Eye className="w-5 h-5" />
                    Processing Results
                  </span>
                  <Badge variant="outline">
                    {processingResults.filter(r => r.success).length}/{processingResults.length} Success
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 max-h-64 overflow-y-auto">
                  {processingResults.map((result, idx) => (
                    <div key={idx} className="flex items-start gap-4 p-3 rounded-lg border">
                      {result.success ? (
                        <>
                          <CheckCircle className="w-5 h-5 text-green-500 mt-1 flex-shrink-0" />
                          <div className="flex-1">
                            <div className="font-medium capitalize">{result.type} - Success</div>
                            {result.original && (
                              <div className="mt-2 grid grid-cols-2 gap-2">
                                <div>
                                  <Label className="text-xs">Original</Label>
                                  <div className="aspect-square rounded overflow-hidden border">
                                    <img
                                      src={result.original}
                                      alt="Original"
                                      className="w-full h-full object-cover"
                                    />
                                  </div>
                                </div>
                                <div>
                                  <Label className="text-xs">Processed</Label>
                                  <div className="aspect-square rounded overflow-hidden border">
                                    <img
                                      src={result.processed}
                                      alt="Processed"
                                      className="w-full h-full object-cover"
                                    />
                                  </div>
                                </div>
                              </div>
                            )}
                            <div className="flex gap-2 mt-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => window.open(result.processed, '_blank')}
                              >
                                <Download className="w-3 h-3 mr-1" />
                                Download
                              </Button>
                              {onProcessComplete && (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => onProcessComplete(result.processed)}
                                >
                                  <Zap className="w-3 h-3 mr-1" />
                                  Use This
                                </Button>
                              )}
                            </div>
                          </div>
                        </>
                      ) : (
                        <>
                          <AlertCircle className="w-5 h-5 text-red-500 mt-1 flex-shrink-0" />
                          <div className="flex-1">
                            <div className="font-medium capitalize">{result.type} - Failed</div>
                            <div className="text-sm text-red-500">{result.error}</div>
                          </div>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default FaceFusionProcessor;
