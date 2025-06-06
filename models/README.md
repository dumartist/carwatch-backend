# Model Files Directory

This directory should contain the following YOLO model files for the CarWatch OCR system to work:

## Required Files

1. **`best_LPD.pt`** - License Plate Detection model
   - Used for detecting license plates in images
   - YOLOv8 model trained for license plate detection

2. **`best_OCR.pt`** - Optical Character Recognition model  
   - Used for recognizing characters on detected license plates
   - YOLOv8 model trained for character recognition

## File Structure
```
models/
├── best_LPD.pt     # License Plate Detection model (REQUIRED)
├── best_OCR.pt     # Character Recognition model (REQUIRED)
└── README.md       # This file
```

## Notes

- These files are required for the OCR functionality to work
- The application will start without them but OCR endpoints will fail
- Model files are typically large (50MB+) and should not be committed to git
- Place your trained YOLO model files in this directory before running the application

## Getting Model Files

If you don't have these files:
1. Train your own YOLOv8 models for license plate detection and OCR
2. Obtain pre-trained models from your team/organization
3. Contact the project maintainer for access to the trained models
