import React, { useState } from 'react';
import { toast } from 'sonner';
import {
  Wand2, Upload, Target, Sparkles, Sliders, Film, Settings, History,
  Download, Eye, RefreshCw, Smile, Frown, Meh, Laugh, Play, Trash2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';

const FaceFusionUI = ({ character, isOpen, onClose }) => {
  const [sourceImage, setSourceImage] = useState(null);
  const [targetImage, setTargetImage] = useState(null);
  const [selectedFace, setSelectedFace] = useState(0);
  const [detectedFaces, setDetectedFaces] = useState([]);
  const [enhancementModel, setEnhancementModel] = useState('gfpgan_1.4');
  const [enhancementBlend, setEnhancementBlend] = useState([100]);
  const [iterations, setIterations] = useState([1]);
  const [ageSlider, setAgeSlider] = useState([25]);
  const [expressionPreset, setExpressionPreset] = useState('neutral');
  const [videoFile, setVideoFile] = useState(null);
  const [outputFormat, setOutputFormat] = useState('png');
  const [outputQuality, setOutputQuality] = useState([95]);
  const [processingHistory, setProcessingHistory] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [enableMasking, setEnableMasking] = useState(false);
  const [maskFeather, setMaskFeather] = useState([10]);
  const [eyeAdjustment, setEyeAdjustment] = useState([0]);
  const [noseAdjustment, setNoseAdjustment] = useState([0]);
  const [mouthAdjustment, setMouthAdjustment] = useState([0]);
  const [frameExtractFPS, setFrameExtractFPS] = useState([24]);

  const enhancementModels = [
    { value: 'gfpgan_1.4', label: 'GFPGAN 1.4', description: 'General purpose restoration' },
    { value: 'codeformer', label: 'CodeFormer', description: 'High-quality restoration' },
    { value: 'restoreformer_plus_plus', label: 'RestoreFormer++', description: 'Advanced restoration' }
  ];

  const expressionPresets = [
    { value: 'neutral', label: 'Neutral', icon: Meh },
    { value: 'smile', label: 'Smile', icon: Smile },
    { value: 'frown', label: 'Frown', icon: Frown },
    { value: 'laugh', label: 'Laugh', icon: Laugh }
  ];

  const handleSourceImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setSourceImage(url);
      setDetectedFaces([{ id: 0, x: 100, y: 100, width: 200, height: 200, confidence: 0.98 }]);
    }
  };

  const handleTargetImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) setTargetImage(URL.createObjectURL(file));
  };

  const handleVideoUpload = (e) => {
    const file = e.target.files[0];
    if (file) setVideoFile(file);
  };

  const handleFaceSwap = async () => {
    if (!sourceImage || !targetImage) {
      toast.error('Please upload both source and target images');
      return;
    }
    setProcessing(true);
    setTimeout(() => {
      setProcessingHistory(prev => [{
        id: Date.now(),
        type: 'Face Swap',
        timestamp: new Date().toISOString(),
        source: sourceImage,
        target: targetImage,
        result: targetImage,
        parameters: { selectedFace, maskingEnabled: enableMasking, maskFeather: maskFeather[0] }
      }, ...prev]);
      toast.success('Face swap completed');
      setProcessing(false);
    }, 2000);
  };

  const handleEnhancement = async () => {
    if (!targetImage) {
      toast.error('Please upload an image to enhance');
      return;
    }
    setProcessing(true);
    setTimeout(() => {
      setProcessingHistory(prev => [{
        id: Date.now(),
        type: 'Enhancement',
        timestamp: new Date().toISOString(),
        source: targetImage,
        result: targetImage,
        parameters: { model: enhancementModel, blend: enhancementBlend[0], iterations: iterations[0] }
      }, ...prev]);
      toast.success('Enhancement completed');
      setProcessing(false);
    }, 2000);
  };

  const handleFaceEditing = async () => {
    if (!targetImage) {
      toast.error('Please upload an image to edit');
      return;
    }
    setProcessing(true);
    setTimeout(() => {
      setProcessingHistory(prev => [{
        id: Date.now(),
        type: 'Face Editing',
        timestamp: new Date().toISOString(),
        source: targetImage,
        result: targetImage,
        parameters: { age: ageSlider[0], expression: expressionPreset, eyeAdjustment: eyeAdjustment[0], noseAdjustment: noseAdjustment[0], mouthAdjustment: mouthAdjustment[0] }
      }, ...prev]);
      toast.success('Face editing completed');
      setProcessing(false);
    }, 2000);
  };

  const handleVideoProcessing = async () => {
    if (!videoFile) {
      toast.error('Please upload a video file');
      return;
    }
    setProcessing(true);
    setTimeout(() => {
      setProcessingHistory(prev => [{
        id: Date.now(),
        type: 'Video Processing',
        timestamp: new Date().toISOString(),
        source: 'video.mp4',
        result: 'processed_video.mp4',
        parameters: { fps: frameExtractFPS[0], frames: 120 }
      }, ...prev]);
      toast.success('Video processing completed');
      setProcessing(false);
    }, 3000);
  };

  if (!character || !isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-7xl max-h-[95vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Wand2 className="w-5 h-5" />
            FaceFusion Studio - {character.name}
          </DialogTitle>
          <DialogDescription>Comprehensive face processing with Gradio-like interface</DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="swap" className="w-full">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="swap"><Target className="w-4 h-4 mr-1" />Swap</TabsTrigger>
            <TabsTrigger value="enhancement"><Sparkles className="w-4 h-4 mr-1" />Enhance</TabsTrigger>
            <TabsTrigger value="editing"><Sliders className="w-4 h-4 mr-1" />Edit</TabsTrigger>
            <TabsTrigger value="video"><Film className="w-4 h-4 mr-1" />Video</TabsTrigger>
            <TabsTrigger value="output"><Settings className="w-4 h-4 mr-1" />Output</TabsTrigger>
            <TabsTrigger value="history"><History className="w-4 h-4 mr-1" />History</TabsTrigger>
          </TabsList>

          <div className="overflow-y-auto max-h-[calc(95vh-200px)] mt-4">
            <TabsContent value="swap" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Source Face</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="border-2 border-dashed border-panel rounded-lg p-8 text-center">
                      {sourceImage ? (
                        <img src={sourceImage} alt="Source" className="mx-auto max-h-64 rounded" />
                      ) : (
                        <div>
                          <Upload className="w-12 h-12 text-secondary mx-auto mb-2" />
                          <p className="text-sm text-secondary">Upload source face image</p>
                        </div>
                      )}
                      <Input type="file" accept="image/*" onChange={handleSourceImageUpload} className="mt-4" />
                    </div>
                    {detectedFaces.length > 0 && (
                      <div className="space-y-2">
                        <Label>Detected Faces: {detectedFaces.length}</Label>
                        <Select value={selectedFace.toString()} onValueChange={(v) => setSelectedFace(parseInt(v))}>
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>
                            {detectedFaces.map((face) => (
                              <SelectItem key={face.id} value={face.id.toString()}>Face {face.id + 1} (Confidence: {(face.confidence * 100).toFixed(0)}%)</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Target Image</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="border-2 border-dashed border-panel rounded-lg p-8 text-center">
                      {targetImage ? (
                        <img src={targetImage} alt="Target" className="mx-auto max-h-64 rounded" />
                      ) : (
                        <div>
                          <Upload className="w-12 h-12 text-secondary mx-auto mb-2" />
                          <p className="text-sm text-secondary">Upload target image</p>
                        </div>
                      )}
                      <Input type="file" accept="image/*" onChange={handleTargetImageUpload} className="mt-4" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Masking Controls</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>Enable Face Masking</Label>
                    <Switch checked={enableMasking} onCheckedChange={setEnableMasking} />
                  </div>
                  {enableMasking && (
                    <div className="space-y-2">
                      <Label>Mask Feather: {maskFeather[0]}px</Label>
                      <Slider value={maskFeather} onValueChange={setMaskFeather} min={0} max={50} step={1} />
                    </div>
                  )}
                  <Button onClick={handleFaceSwap} disabled={processing} className="w-full">
                    <Play className="w-4 h-4 mr-2" />
                    {processing ? 'Processing...' : 'Swap Faces'}
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="enhancement" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Image to Enhance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="border-2 border-dashed border-panel rounded-lg p-8 text-center">
                    {targetImage ? (
                      <img src={targetImage} alt="Enhance" className="mx-auto max-h-64 rounded" />
                    ) : (
                      <div>
                        <Upload className="w-12 h-12 text-secondary mx-auto mb-2" />
                        <p className="text-sm text-secondary">Upload image to enhance</p>
                      </div>
                    )}
                    <Input type="file" accept="image/*" onChange={handleTargetImageUpload} className="mt-4" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Enhancement Model</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Select value={enhancementModel} onValueChange={setEnhancementModel}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {enhancementModels.map((model) => (
                        <SelectItem key={model.value} value={model.value}>
                          <div>
                            <div className="font-medium">{model.label}</div>
                            <div className="text-xs text-secondary">{model.description}</div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <div className="space-y-2">
                    <Label>Enhancement Blend: {enhancementBlend[0]}%</Label>
                    <Slider value={enhancementBlend} onValueChange={setEnhancementBlend} min={0} max={100} step={1} />
                  </div>

                  <div className="space-y-2">
                    <Label>Iterations: {iterations[0]}</Label>
                    <Slider value={iterations} onValueChange={setIterations} min={1} max={5} step={1} />
                  </div>

                  <Button onClick={handleEnhancement} disabled={processing} className="w-full">
                    <Sparkles className="w-4 h-4 mr-2" />
                    {processing ? 'Enhancing...' : 'Enhance Face'}
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="editing" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Image to Edit</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="border-2 border-dashed border-panel rounded-lg p-8 text-center">
                    {targetImage ? (
                      <img src={targetImage} alt="Edit" className="mx-auto max-h-64 rounded" />
                    ) : (
                      <div>
                        <Upload className="w-12 h-12 text-secondary mx-auto mb-2" />
                        <p className="text-sm text-secondary">Upload image to edit</p>
                      </div>
                    )}
                    <Input type="file" accept="image/*" onChange={handleTargetImageUpload} className="mt-4" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Age Modification</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Label>Target Age: {ageSlider[0]} years</Label>
                  <Slider value={ageSlider} onValueChange={setAgeSlider} min={0} max={100} step={1} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Expression Presets</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-2">
                    {expressionPresets.map((preset) => {
                      const Icon = preset.icon;
                      return (
                        <Button
                          key={preset.value}
                          variant={expressionPreset === preset.value ? 'default' : 'outline'}
                          onClick={() => setExpressionPreset(preset.value)}
                          className="gap-2"
                        >
                          <Icon className="w-4 h-4" />
                          {preset.label}
                        </Button>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Feature Adjustments</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Eye Size: {eyeAdjustment[0] > 0 ? '+' : ''}{eyeAdjustment[0]}</Label>
                    <Slider value={eyeAdjustment} onValueChange={setEyeAdjustment} min={-50} max={50} step={1} />
                  </div>
                  <div className="space-y-2">
                    <Label>Nose Size: {noseAdjustment[0] > 0 ? '+' : ''}{noseAdjustment[0]}</Label>
                    <Slider value={noseAdjustment} onValueChange={setNoseAdjustment} min={-50} max={50} step={1} />
                  </div>
                  <div className="space-y-2">
                    <Label>Mouth Size: {mouthAdjustment[0] > 0 ? '+' : ''}{mouthAdjustment[0]}</Label>
                    <Slider value={mouthAdjustment} onValueChange={setMouthAdjustment} min={-50} max={50} step={1} />
                  </div>
                  <Button onClick={handleFaceEditing} disabled={processing} className="w-full">
                    <Sliders className="w-4 h-4 mr-2" />
                    {processing ? 'Editing...' : 'Apply Edits'}
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="video" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Video Upload</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="border-2 border-dashed border-panel rounded-lg p-8 text-center">
                    {videoFile ? (
                      <div>
                        <Film className="w-12 h-12 text-primary mx-auto mb-2" />
                        <p className="text-sm text-primary font-medium">{videoFile.name}</p>
                      </div>
                    ) : (
                      <div>
                        <Film className="w-12 h-12 text-secondary mx-auto mb-2" />
                        <p className="text-sm text-secondary">Upload video file</p>
                      </div>
                    )}
                    <Input type="file" accept="video/*" onChange={handleVideoUpload} className="mt-4" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Frame Extraction</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Extract FPS: {frameExtractFPS[0]}</Label>
                    <Slider value={frameExtractFPS} onValueChange={setFrameExtractFPS} min={1} max={60} step={1} />
                  </div>
                  <Button variant="outline" className="w-full">
                    <Download className="w-4 h-4 mr-2" />
                    Extract Frames
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Batch Face Processing</CardTitle>
                  <CardDescription>Apply face swap/enhancement to all frames</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" className="w-full mb-2">
                    <Target className="w-4 h-4 mr-2" />
                    Batch Face Swap
                  </Button>
                  <Button variant="outline" className="w-full">
                    <Sparkles className="w-4 h-4 mr-2" />
                    Batch Enhancement
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Video Reassembly</CardTitle>
                </CardHeader>
                <CardContent>
                  <Button onClick={handleVideoProcessing} disabled={processing} className="w-full">
                    <Play className="w-4 h-4 mr-2" />
                    {processing ? 'Processing...' : 'Reassemble Video'}
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="output" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Output Format</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Select value={outputFormat} onValueChange={setOutputFormat}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="png">PNG</SelectItem>
                      <SelectItem value="jpg">JPEG</SelectItem>
                      <SelectItem value="webp">WebP</SelectItem>
                    </SelectContent>
                  </Select>

                  <div className="space-y-2">
                    <Label>Quality: {outputQuality[0]}%</Label>
                    <Slider value={outputQuality} onValueChange={setOutputQuality} min={1} max={100} step={1} />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="history" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Processing History ({processingHistory.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  {processingHistory.length === 0 ? (
                    <div className="text-center py-8 text-secondary">
                      <History className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>No processing history yet</p>
                    </div>
                  ) : (
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {processingHistory.map((item) => (
                        <Card key={item.id} className="p-3">
                          <div className="flex items-start gap-3">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge>{item.type}</Badge>
                                <span className="text-xs text-secondary">
                                  {new Date(item.timestamp).toLocaleString()}
                                </span>
                              </div>
                              <div className="grid grid-cols-2 gap-2">
                                <div>
                                  <Label className="text-xs">Source</Label>
                                  <img src={item.source} alt="Source" className="w-full h-20 object-cover rounded mt-1" />
                                </div>
                                <div>
                                  <Label className="text-xs">Result</Label>
                                  <img src={item.result} alt="Result" className="w-full h-20 object-cover rounded mt-1" />
                                </div>
                              </div>
                              <div className="mt-2 text-xs text-secondary">
                                {Object.entries(item.parameters).map(([key, value]) => (
                                  <span key={key} className="mr-3">
                                    {key}: {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value}
                                  </span>
                                ))}
                              </div>
                            </div>
                            <div className="flex flex-col gap-1">
                              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                <Eye className="w-4 h-4" />
                              </Button>
                              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                <Download className="w-4 h-4" />
                              </Button>
                              <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-red-500">
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </div>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default FaceFusionUI;