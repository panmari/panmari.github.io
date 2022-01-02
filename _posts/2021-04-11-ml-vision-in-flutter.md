---
layout: post
title: Make your flutter app detect dogs
tags: [flutter, machine learning, vision, label detection]
---

Changing content displayed for a given camera input stream makes your app feel like magic. I wanted to try my hand at exactly this for [my app](https://play.google.com/store/apps/details?id=ch.panmari.cat_sight) that simulates the vision of a cat.

UPDATE for 2022: turns out my choice lined out below was deprecated rather quickly. The currently recommended package is [google_ml_kit](https://pub.dev/packages/google_ml_kit).

After surveying the situtation for a bit, I found a variety of packages that looked relevant

* Low level API to plug in tensorflow models: [tflite](https://pub.dev/packages/tflite)
* Unofficial ML Kit package: [mlkit](https://pub.dev/packages/mlkit)

To me, the official [ML Vision package for firebase](https://pub.dev/packages/firebase_ml_vision) seemed most promising because:

1. Model is on device and easy to install
2. Easy to integrate into an existing flutter app
3. Option to switch to a custom model in the future using [firebae_ml_custom](https://pub.dev/packages/firebase_ml_custom)

It didn't take long until I ran into the first complication. When trying the example app for the `firebase_ml_vision` image labeler, my test phone (a Pixel 3a) only ever produced the labels `metal` and `pattern`.

![Screenshot of the example ML vision app only detecting bad patterns](/assets/img/flutter_ml_vision/example_fail_labels.png)

When working with ML models previously, I had similar issues when the input was garbled. For example when the image width was set too small and pixels from line `n` leaked onto line `n+1`. I didn't have to search far until I found others with the same issue ([opensource ftw!](https://github.com/FirebaseExtended/flutterfire/issues/1518#issuecomment-614684648)). According to the comment by *benjastudio*, this behavior was indeed caused by some phones adding additional padding to their image data for certain resolution settings.

I implemented the workaround described by *benjastudio* and boom: The detector started returning reasonable labels. But I didn't want to keep employing workarounds: They are brittle and break in the future when the underlying assumptions change. Instead, I [sent a PR](https://github.com/FirebaseExtended/flutterfire/pull/5711) to the owners of the repository. Review still pending!

For now, I'm using my patched version of the `firebase_ml_vision`, detecting dogs reliably.

![Cat Vision app with dog detected](/assets/img/flutter_ml_vision/dog_detected.png)
