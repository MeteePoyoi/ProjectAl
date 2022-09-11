import os
import numpy as np
import pandas as pd
import argparse
from sklearn.preprocessing import LabelEncoder

# disable tensorflow INFO
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"

import tensorflow as tf  # noqa: E402
import tensorflow_hub as hub  # noqa: E402
import tensorflow_text  # Important: needed but not used # noqa: E402 F401


def load_encoder(url):
    # load encoder model
    print(f"... loading encoder from {url}")
    return hub.load(url)


def import_dataset(data_file, encoder, label_file):
    print(f"... importing keywords from {data_file}")

    df = pd.read_csv(data_file)
    print(df.head(10))

    # encode intent_id into value 0...n_classes-1
    intents = df["intent_id"]
    keywords = df["keyword"]

    le = LabelEncoder()
    le.fit(intents)
    labels = le.transform(intents)

    print(f"... total classes = {len(le.classes_)}")
    print(le.classes_)

    # save labels to use when predict
    le.classes_.dump(label_file + "_labels.pickle")

    features = []

    # embedding keywords into features
    print("... embedding keywords", end="")
    for i, keyword in enumerate(keywords):
        print(".", end="")
        embed = encoder(keyword)
        features.append(embed)

    print(f"... embed {len(keywords)} keywords")
    return {
        "features": features,
        "labels": labels,
        "intents": intents,
        "classes": le.classes_,
    }


def prepare_tf_dataset(features, labels, intents):
    features = np.array(features)
    labels = np.array(labels)

    # doing one-hot encode for label
    labels_onehot = np.zeros([labels.size, labels.max() + 1])
    labels_onehot[np.arange(labels.size), labels] = 1

    print(f"... features shape = {features.shape}")
    print(f"... labels onehot shape = {labels_onehot.shape}")

    dataset = tf.data.Dataset.from_tensor_slices((features, labels_onehot))

    # shuffle_buffer_size >= dataset size
    shuffle_buffer_size = 1000
    dataset = dataset.shuffle(shuffle_buffer_size)

    test_size = 0.1
    batch_size = 16

    test_samples = round(test_size * len(intents))

    train_ds = dataset.skip(test_samples)
    test_ds = dataset.take(test_samples)

    train_ds = train_ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    test_ds = test_ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)

    return train_ds, test_ds


def create_model(class_names):
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Bidirectional(
                tf.keras.layers.LSTM(128, return_sequences=True),
                input_shape=(1, 512),
            ),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(len(class_names), activation="softmax"),
        ]
    )

    return model


def parse_commandline():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-d", "--data", required=True, help="data file in CSV format"
    )
    parser.add_argument(
        "-s", "--save-model", required=True, help="path to save trained model"
    )
    parser.add_argument(
        "-l", "--load-model", help="path to load previously trained model"
    )
    parser.add_argument(
        "-e",
        "--encoder",
        help="URL to load text encoder",
        default="https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3",  # noqa: E501
    )

    return vars(parser.parse_args())


def main():
    opts = parse_commandline()  # get command line arguments
    print(opts)

    # load Universal Sentence Encoder from tensorflow hub
    encoder = load_encoder(opts["encoder"])

    # import csv file and return dict
    # {
    #   "features": features,
    #   "labels": labels,
    #   "intents": intents,
    #   "classes": class_names
    # }
    dataset = import_dataset(opts["data"], encoder, opts["save_model"])

    # prepare dataset for tensorflow and return train_dataset, test_dataset
    train_ds, test_ds = prepare_tf_dataset(
        dataset["features"], dataset["labels"], dataset["intents"]
    )
    load_model = opts["load_model"]

    if load_model is None:
        print("... create new model")
        model = create_model(dataset["classes"])
        model.compile(
            loss="categorical_crossentropy",
            optimizer="adam",
            metrics=["accuracy"],
        )
    else:
        print(f"... load model from {opts['load_model']}")
        model = tf.keras.models.load_model(load_model)

    # define callback before training
    callbacks = []
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        min_delta=0,
        patience=10,
        verbose=1,
        restore_best_weights=True,
        mode="auto",
    )

    callbacks.append(early_stop)

    model.summary()

    # do actual training
    epochs = 50000000  # With callbacks this can be arbitrarily large
    model.fit(
        train_ds, epochs=epochs, validation_data=test_ds, callbacks=callbacks
    )

    # save model
    model.save(opts["save_model"])

    print(f"... training done, model is saved to {opts['save_model']}")


if __name__ == "__main__":
    main()
