#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import cv2
import numpy as np
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from matplotlib import pyplot as plt


class TOD(object):
    def __init__(self):
        # Path to frozen detection graph. This is the actual model that is used for the object detection.
        self.PATH_TO_CKPT = 'data/frozen_inference_graph.pb/frozen_inference_graph.pb'
        # List of the strings that is used to add correct label for each box.
        self.PATH_TO_LABELS = 'data/label_map.pbtxt'
        # 分类数量
        self.NUM_CLASSES = 1

        self.detection_graph = self._load_model()
        self.category_index = self._load_label_map()

    def _load_model(self):
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
        return detection_graph

    def _load_label_map(self):
        label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=self.NUM_CLASSES, use_display_name=True)
        category_index = label_map_util.create_category_index(categories)
        return category_index

    def detect(self, image,path):
        os.environ["CUDA_VISIBLE_DEVICES"] = "3"
        tf.device('/gpu:3')
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.4)
        config = tf.ConfigProto(allow_soft_placement=True, gpu_options=gpu_options)
        with self.detection_graph.as_default():
            with tf.Session(graph=self.detection_graph) as sess:
                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(image, axis=0)
                image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
                # Each box represents a part of the image where a particular object was detected.
                boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
                # Each score represent how level of confidence for each of the objects.
                # Score is shown on the result image, together with the class label.
                scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
                classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
                # Actual detection.
                (boxes, scores, classes, num_detections) = sess.run(
                    [boxes, scores, classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})
                # Visualization of the results of a detection.
                vis_util.visualize_boxes_and_labels_on_image_array(
                    image,
                    np.squeeze(boxes),
                    np.squeeze(classes).astype(np.int32),
                    np.squeeze(scores),
                    self.category_index,
                    use_normalized_coordinates=True,
                    line_thickness=8)
        # path = os.path.join(path, i)
        cv2.imwrite(os.path.join(path, 'your_image.jpg'), image)
        # plt.imshow(image)
        # plt.show()


if __name__ == '__main__':

    detecotr = TOD()

    img_path = 'images/test'
    for i in os.listdir(img_path):
        if i.endswith('.jpg'):
            path = os.path.join(img_path, i)
            image = cv2.imread(path)
            detecotr.detect(image,img_path)