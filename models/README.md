# Model Files Directory

This directory contains the YOLO model files for the CarWatch OCR system to function properly.

## Required Files

### 1. **`best_LPD.pt`** - License Plate Detection Model
- **Purpose**: Detects license plates in vehicle images
- **Architecture**: YOLOv8 optimized for license plate detection
- **Dataset**: 6000+ annotated images
- **Performance**: Consistent and reliable detection rate
- **Training Details**: 
  - Optimized for most lighting conditions and plate orientations

### 2. **`best_OCR.pt`** - Optical Character Recognition Model (Updated)
- **Purpose**: Recognizes characters on detected license plates
- **Architecture**: YOLOv8 trained for character recognition
- **Dataset**: 1000+ annotated character images (recently improved)
- **Performance**: Enhanced character recognition accuracy
- **Training Details**:
  - Supports alphanumeric character recognition
- **Last Updated**: June 15, 2025

## File Structure
```
models/
├── best_LPD.pt     # License Plate Detection model (REQUIRED)
├── best_OCR.pt     # Character Recognition model (REQUIRED) - Updated v2.0
└── README.md       # This documentation
```


## Model Performance Improvements

### Optical Character Recognition (best_OCR.pt)
- **Dataset Improvement**: Enhanced with better quality annotated character images
- **Improved Accuracy**: Better character recognition rates across various scenarios
- **Enhanced Robustness**: Better performance in challenging conditions:
  - Blurry or low-resolution plate text
  - Various font styles and character spacing
  - Different lighting conditions affecting text clarity
  - Worn or damaged license plates

### License Plate Detection (best_LPD.pt)
- **Stable Performance**: Proven detection capabilities with 6000+ training images
- **Reliable Detection**: Consistent performance across various vehicle types and conditions

### Expected Performance Metrics
- **Detection Rate**: ~95%+ for clear, unobstructed plates (LPD)
- **Character Recognition**: Improved accuracy for text extraction (OCR)
- **Processing Speed**: Optimized inference time for both models
- **Memory Usage**: Efficient deployment with ~6MB model sizes

## Training Performance

### OCR Model Training Metrics
The following chart shows the training performance of the updated OCR model, demonstrating convergence and validation accuracy:

![OCR Training Metrics](https://drive.google.com/uc?export=view&id=14c9GB7Jk3pkKM_ELS65EDP55r96RPWg6)

*Training metrics showing box loss, classification loss, precision, recall, and mAP scores across epochs*

## Model Detection Examples

### Real-world Performance
Here are examples of the OCR model in action, showing character detection and recognition on various license plates:

![OCR Detection Examples](https://drive.google.com/uc?export=view&id=1i1CZM7HADb9Tfl-qUL_-dGmyP_LeaWy1)

*Examples showing character-level detection with bounding boxes and confidence scores on different license plate types*

## Usage in Application

The models are automatically loaded when the application starts:

python
# License Plate Detection
detect_and_crop_plate(image)  # Uses best_LPD.pt

# Character Recognition  
recognize_characters_with_yolo(cropped_plate)  # Uses best_OCR.pt


## Model Specifications

| Model | File Size | Input Size | Classes | Dataset Size |
|-------|-----------|------------|---------|--------------|
| best_LPD.pt | ~6MB | 640x640 | 1 (plate) | 6000+ images |
| best_OCR.pt | ~6MB | 640x640 | 36 (A-Z, 0-9) | 1000+ images |

## Notes

- These files are **required** for the OCR functionality to work
- The application will start without them but OCR endpoints will return default values
- Place your trained YOLO model files in this directory before running the application
- **Latest Update**: OCR model improved for better character recognition accuracy

## Getting Model Files

If you don't have these files:
1. **Train your own models**: Use YOLOv8 with your specific dataset
2. **Obtain from team**: Contact your project team for the latest model files
3. **Project maintainer**: Contact the CarWatch development team for access
4. **Validation**: Ensure models are compatible with YOLOv8 architecture

## Troubleshooting

### Model Loading Issues
bash
# Verify model files exist and are accessible
ls -la models/
# Expected files: best_LPD.pt, best_OCR.pt

# Test model loading
python -c "from ultralytics import YOLO; model = YOLO('models/best_LPD.pt'); print('LPD model loaded successfully')"
python -c "from ultralytics import YOLO; model = YOLO('models/best_OCR.pt'); print('OCR model loaded successfully')"


### Performance Issues
- Ensure sufficient system memory (2GB+ recommended)
- Check GPU availability for faster inference
- Monitor model loading time during application startup

---
**Model Version**: LPD v1.0 (6000+ dataset), OCR v2.0 (improved)  
**Last Updated**: June 15, 2025  
**Compatibility**: YOLOv8, Ultralytics 8.0.225+