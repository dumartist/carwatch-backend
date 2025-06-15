# Model Files Directory

This directory contains the YOLO model files for the CarWatch OCR system to function properly.

## Required Files

### 1. **`best_LPD.pt`** - License Plate Detection Model (Updated)
- **Purpose**: Detects license plates in vehicle images
- **Architecture**: YOLOv8 optimized for license plate detection
- **Dataset**: 6000+ annotated images (significantly upgraded from 500 images)
- **Performance**: Enhanced accuracy and detection rate
- **Last Updated**: June 15, 2025

### 2. **`best_OCR.pt`** - Optical Character Recognition Model
- **Purpose**: Recognizes characters on detected license plates
- **Architecture**: YOLOv8 trained for character recognition
- **Dataset**: 1000+ annotated character images

## File Structure
```
models/
├── best_LPD.pt     # License Plate Detection model (REQUIRED) - Updated v2.0
├── best_OCR.pt     # Character Recognition model (REQUIRED)
└── README.md       # This documentation
```


## Model Performance Improvements

### License Plate Detection (best_LPD.pt)
- **Dataset Expansion**: Increased from 500 to 6000+ annotated images (12x improvement)
- **Improved Accuracy**: Better detection rates across various scenarios
- **Enhanced Robustness**: Better performance in challenging conditions:
  - Low-light environments
  - Various plate orientations and angles
  - Different vehicle types and distances
  - Weather conditions (rain, fog, bright sunlight)

### Expected Performance Metrics
- **Detection Rate**: ~95%+ for clear, unobstructed plates
- **Processing Speed**: 20-30% faster than previous version
- **False Positive Rate**: Significantly reduced
- **Memory Usage**: Optimized for production deployment (~6MB model size)

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
| best_OCR.pt | ~6MB | 800x800 | 36 (A-Z, 0-9) | 1000+ images |

## Notes

- These files are **required** for the OCR functionality to work
- The application will start without them but OCR endpoints will return default values
- Place your trained YOLO model files in this directory before running the application
- **Latest Update**: LPD model improved with 12x larger dataset for significantly better accuracy

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
**Model Version**: LPD v2.0 (6000+ dataset), OCR v1.0  
**Last Updated**: June 15, 2025  
**Compatibility**: YOLOv8, Ultralytics 8.0.225+