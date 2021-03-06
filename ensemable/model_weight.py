import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import tensorflow as tf
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)

from config import *
import keras
import keras.backend as K
from utils.data import *
from utils.preprocess import *
from keras.layers import *
from keras.models import *
from keras.optimizers import *
from keras.callbacks import *

pred_list = [
    "%s_char_cnn_boosting.pred",
    "%s_word_cnn_boosting.pred",
    "%s_fasttext_boosting.pred",
]
val = pd.read_csv(Config.cache_dir+"/val.csv", sep="\t")
val_label = get_labels(val.label)

model_count = len(pred_list)
data = np.zeros(shape=(val.shape[0], 2, model_count))
for i,v in enumerate(pred_list):
    data[:,:,i] = np.load(Config.cache_dir + "/" + v%"val")

datainput = Input(shape=(1999, model_count))
output = Activation(activation="sigmoid")(Reshape((1999,))(Conv1D(1, 1, kernel_initializer="ones", use_bias=True, name="model_weight")(datainput)))
model = Model(inputs=datainput,outputs=output)
model.compile(loss='categorical_crossentropy',optimizer="sgd",metrics=['accuracy'])

model.fit(data, val_label, validation_split=0.1, epochs=12)

pred = model.predict(data)
p,r,f1 = map_score(pred)
print(p,r,f1)
print(model.get_layer("model_weight").get_weights())

test = get_test_data()
test_data = np.zeros(shape=(test.shape[0], 1999, model_count))
for i,v in enumerate(pred_list):
    test_data[:,:,i] = np.load(Config.cache_dir + "/" + v%"test")

test_pred = model.predict(test_data)
submit(test_pred)