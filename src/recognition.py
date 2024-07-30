import cv2
import os
import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "0"
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = "0"
import numpy as np
import pickle
import src.facenet as facenet
import src.align.detect_face as align
import collections
import tensorflow.compat.v1 as tf
import imutils
import time

# model, class_names,images_placeholder, embeddings, sess = None, None, None, None, None

CLASSIFIER_PATH = os.path.join(os.getcwd(), 'models/classifier.pkl')
FACENET_MODEL_PATH = os.path.join(os.getcwd(), 'models/20180402-114759.pb')
MINSIZE = 20
THRESHOLD = [0.6, 0.7, 0.7]
FACTOR = 0.709
IMAGE_SIZE = 182
INPUT_IMAGE_SIZE = 160
GPU_MEMORY_FRACTION = 1.0
RATE_ACCURACY = 0.9
person_detected = collections.Counter()


def preprocess_frame(frame):
    
    return frame

# Load your model here
def load_model():
    # Load The Custom Classifier
    with open(CLASSIFIER_PATH, 'rb') as file:
        model, class_names,_,__= pickle.load(file)
    print("Custom Classifier, Successfully loaded")
    return model, class_names

def load_facenet():
    with tf.Graph().as_default():
        # Cai dat GPU neu co
        gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=GPU_MEMORY_FRACTION)
        sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options, log_device_placement=False))

        with sess.as_default():
            # Load the model
            print('Loading feature extraction model')
            facenet.load_model(FACENET_MODEL_PATH)

            # Get input and output tensors
            images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
            pnet, rnet, onet = align.create_mtcnn(sess, "src/align")
            person_detected = collections.Counter()
    return images_placeholder, phase_train_placeholder, embeddings, sess, pnet, rnet, onet

def recognition_face(frame, model, class_names, images_placeholder, phase_train_placeholder, embeddings, sess, pnet, rnet, onet, paint=True, rate_accuracy=RATE_ACCURACY):

    frame = preprocess_frame(frame)

    bounding_boxes, _ = align.detect_face(frame, MINSIZE, pnet, rnet, onet, THRESHOLD, FACTOR)
    faces_found = bounding_boxes.shape[0]
    try: 
        # if faces_found > 1:
        #     cv2.putText(frame, "Only one face", (0, 100), cv2.FONT_HERSHEY_COMPLEX_SMALL,
        #                 1, (255, 255, 255), thickness=1, lineType=2)
        # elif faces_found > 0:
        if faces_found > 0:
            det = bounding_boxes[:, 0:4]
            bb = np.zeros((faces_found, 4), dtype=np.int32)
            persons_d = []
            for i in range(faces_found):
                bb[i][0] = det[i][0]
                bb[i][1] = det[i][1]
                bb[i][2] = det[i][2]
                bb[i][3] = det[i][3]
                # print(bb[i][3]-bb[i][1])
                # print(frame.shape[0])
                # print((bb[i][3]-bb[i][1])/frame.shape[0])
                if (bb[i][3]-bb[i][1])/frame.shape[0]>0.25:
                    cropped = frame[bb[i][1]:bb[i][3], bb[i][0]:bb[i][2], :]
                    scaled = cv2.resize(cropped, (INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE),
                                        interpolation=cv2.INTER_CUBIC)
                    scaled = facenet.prewhiten(scaled)
                    scaled_reshape = scaled.reshape(-1, INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE, 3)
                    feed_dict = {images_placeholder: scaled_reshape, phase_train_placeholder: False}
                    emb_array = sess.run(embeddings, feed_dict=feed_dict)

                    predictions = model.predict_proba(emb_array)
                    best_class_indices = np.argmax(predictions, axis=1)
                    best_class_probabilities = predictions[
                        np.arange(len(best_class_indices)), best_class_indices]
                    best_name = class_names[best_class_indices[0]]
                    # print("Name: {}, Probability: {}".format(best_name, best_class_probabilities))
                    # if best_class_probabilities < 0.8:
                    #     best_name = "Unknown"


                    if paint==True:
                        cv2.rectangle(frame, (bb[i][0], bb[i][1]), (bb[i][2], bb[i][3]), (0, 255, 0), 2)
                        text_x = bb[i][0]
                        text_y = bb[i][3] + 20
                        name = "Unknown"
                        if best_class_probabilities > rate_accuracy:
                            name = class_names[best_class_indices[0]]
                        cv2.putText(frame, name, (text_x, text_y), cv2.FONT_HERSHEY_COMPLEX_SMALL,1, (255, 255, 255), thickness=1, lineType=2)
                        cv2.putText(frame, str(round(best_class_probabilities[0], 3)), (text_x, text_y + 17),cv2.FONT_HERSHEY_COMPLEX_SMALL,1, (255, 255, 255), thickness=1, lineType=2)
                        person_detected[best_name] += 1
                    
                    bbb = [bb[i][0] / frame.shape[1], bb[i][1] / frame.shape[0], bb[i][2] / frame.shape[1], bb[i][3] / frame.shape[0]]
                    persons_d.append({'name':best_name,'accuracy': best_class_probabilities[0],  'x1':bbb[0],'y1': bbb[1],'x2': bbb[2],'y2': bbb[3]} )
                    # return best_name, best_class_probabilities[0], frame, bbb
            persons = {'persons_detected': persons_d, 'img': frame}
            return persons    
        
        return {'persons_detected': [], 'img': frame}
    except:
        return {'persons_detected': [], 'img': frame}
        pass
    

def init():
    global model, class_names, images_placeholder, embeddings, sess, pnet, rnet, onet, phase_train_placeholder
    model, class_names= load_model()
    images_placeholder,phase_train_placeholder, embeddings, sess, pnet, rnet, onet = load_facenet()

def frame_recognition(frame):
    return recognition_face(frame, model, class_names, images_placeholder,phase_train_placeholder, embeddings, sess, pnet, rnet, onet)
