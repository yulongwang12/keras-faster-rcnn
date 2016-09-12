from preprocessing import process_image
from proposal_test_model import load_proposal_model, proposal_test_model
from detection_test_model import load_detection_model, detection_test_model
from caffe_utils import extract_caffe_weights
from fast_rcnn_utils import filter_boxes
from nms import nms
from tools import plot_image_with_bbox
from config import faster_rcnn_voc0712_vgg

import cv2
import numpy as np
import tensorflow as tf

image_name_list = ['1.jpg']
config = faster_rcnn_voc0712_vgg()

try:
    proposal_weights = np.load('models/vgg16_proposal_model.npy')
    detection_weights = np.load('models/vgg16_detection_model.npy')

except:
    proposal_weights = extract_caffe_weights('pretrained_models/proposal_test.prototxt',
                                             'pretrained_models/proposal_final',
                                             'models/vgg16_proposal_model.npy')

    detection_weights = extract_caffe_weights('pretrained_models/detection_test.prototxt',
                                              'pretrained_models/detection_final',
                                              'models/vgg16_detection_model.npy')

proposal_layers = load_proposal_model(proposal_weights)
detection_layers = load_detection_model(detection_weights)

sess = tf.Session()
sess.run(tf.initialize_all_variables())

for name in image_name_list:
    im = cv2.imread(name)[:, :, ::-1]
    im_prec = process_image(im, config.proposal)
    boxes, scores, feats = proposal_test_model(sess, im_prec, proposal_layers, config.proposal)
    boxes = filter_boxes(boxes, scores, config.proposal)

    boxes, scores = detection_test_model(sess, feats, boxes, detection_layers)
    boxes, scores = nms(boxes, scores, config.detection)

    plot_image_with_bbox(im, boxes, scores, config.classes)
