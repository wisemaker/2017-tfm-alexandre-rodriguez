import os
import sys
import threading
from Net import model as modellib
from Net import coco as coco
from Net import visualize as visualize


class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1


class Segmentation_Network():
    ''' Class to create a Mask R-CNN network, Keras-based, trained on COCO dataset.
     At its creation, it imports the weights from the frozen model.'''

    def __init__(self):
        sys.path.append('/home/alexandre/coco/PythonAPI')

        # Root directory of the project
        ROOT_DIR = os.getcwd()

        # Directory to save logs and trained model
        MODEL_DIR = os.path.join(ROOT_DIR, "logs")

        # Local path to trained weights file
        COCO_MODEL_PATH = os.path.join(ROOT_DIR, "Net/mask_rcnn_coco.h5")

        # Create model object in inference mode.
        config = InferenceConfig()
        self.model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

        # Load weights trained on MS-COCO
        self.model.load_weights(COCO_MODEL_PATH, by_name=True)

        print("Network created!")

        self.lock = threading.Lock()

        self.input_image = None
        self.output_image = None

    def segmentation(self):
        # Run detection
        image = self.input_image
        if image is not None:

            results = self.model.detect([image], verbose=1)

            # COCO Class names
            # Index of the class in the list is its ID. For example, to get ID of
            # the teddy bear class, use: class_names.index('teddy bear')
            class_names = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
                           'bus', 'train', 'truck', 'boat', 'traffic light',
                           'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
                           'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
                           'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
                           'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
                           'kite', 'baseball bat', 'baseball glove', 'skateboard',
                           'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
                           'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
                           'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
                           'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
                           'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
                           'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
                           'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
                           'teddy bear', 'hair drier', 'toothbrush']

            # Visualize results
            r = results[0]
            segmented_image = visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'],
                                                          class_names, r['scores'])

        else:
            segmented_image = None

        return segmented_image

    def update(self):
        self.lock.acquire()
        self.output_image = self.segmentation()
        self.lock.release()