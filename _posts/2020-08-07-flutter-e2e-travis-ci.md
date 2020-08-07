---
layout: post
title: Run Flutter e2e tests on Travis CI
tags: [flutter, e2e, integration testing, firebase, camera]
---

Integration tests play an important role in making sure you don't break your app. In this blog post I go over the important bits for writing and end to end integration test in Flutter, then making it run continuously on Travis CI.

## Background

Flutter broadly supports two types of tests

* Unit tests, geared towards testing individual widgets
* Integration tests using the [e2e package](https://pub.dev/packages/e2e), testing the whole app end to end.

There's a lot of documentation about how to make [unit testing work](https://flutter.dev/docs/cookbook/testing/widget/introduction). Also [running such tests on Travis CI](https://medium.com/flutter/test-flutter-apps-on-travis-3fd5142ecd8c) is easily set up with the help of some Google searches.

But information is scarce when it comes to end to end tests. This blog post hopefully improves on that.

## Creating an integration test

First, we need to create the test to run. I won't go into much detail here, as this will be highly app dependent. In a nutshell, end to end tests consist of two separate files in Flutter

1. The runner, the part that drives the test. Usually very simple and situated in `test_driver/your_app_e2e_test.dart`.
2. The actual test. Usually situated in `test/your_app_e2e.dart`.

The [documentation of the e2e package](https://pub.dev/packages/e2e) should get you started in creating the content of these files. Once you have a skeleton, run the test locally.

    # Needs an emulator running or a device connected!
    flutter drive test/your_app_e2e.dart

If your app is more complex, for example involves using the camera, you'll need a more complex test driver. Take inspiration from the [e2e test of the camera plugin](https://github.com/flutter/plugins/blob/master/packages/camera/example/test_driver/camera_e2e_test.dart) to make this work.

## Run integration test directly on Travis CI

Just as when running locally, you need a device or an emulator when running on Travis CI. [Others have succeeded](https://github.com/ankidroid/Anki-Android/blob/master/.travis.yml) in setting up android emulators on Travis CI for a pure android project. I could not get this to work even after multiple attempts, so I gave up and instead looked for alternatives.

## Run integration tests in Firebase Test Lab

The flutter e2e package also advertises running integration tests in Firebase Test Lab. The [free plan](https://firebase.google.com/pricing) allows running up to 10 tests per day, so this seemed like a good alternative. The steps for getting there are a bit more involved, though.

1. If you don't already have one, create a Firebase project in the [Firebase Console](https://console.firebase.google.com/).
1. Set up your flutter project for android device testing, see [instructions](https://pub.dev/packages/e2e#android-device-testing).
1. Generate and download a private service key to authenticate Travis CI for running tests. Starting at the [Firebase Console](https://console.firebase.google.com/), navigate to `Firebase -> Project -> Project Settings -> Service accounts`, then click on Download.
1. Move the key to the root of your repository.
1. [Encrypt the key](https://docs.travis-ci.com/user/encrypting-files/) for Travis CI using the following commands. Take note of the output, you'll need it later for decrypting.
```
gem install travis
travis login --com #login to your account
travis login --org #login to your account
travis encrypt-file key.json --add
```
1. Add the *encrypted* key to your repository.

Now all parts are in place! What's remaining is to update `.travis.yml` to actually run the test.

```yaml
language: android
os:
- linux
sudo: false
android:
  components:
    - tools
    - platform-tools
    - add-on
    - extra
addons:
  apt:
    packages:
    - lib32stdc++6
before_install:
  # Android is needed for building the e2e test for Firebase.
  - touch $HOME/.android/repositories.cfg
  - yes | sdkmanager "platforms;android-28"
  - yes | sdkmanager "build-tools;28.0.3"

install:
# Install gcloud sdk for interacting with Firebase.
- gcloud version || true
- if [ ! -d "$HOME/google-cloud-sdk/bin" ]; then rm -rf $HOME/google-cloud-sdk; export
  CLOUDSDK_CORE_DISABLE_PROMPTS=1; curl https://sdk.cloud.google.com | bash; fi
- source /home/travis/google-cloud-sdk/path.bash.inc
- gcloud version
- git clone https://github.com/flutter/flutter.git -b stable
- "./flutter/bin/flutter doctor"
before_script:
# Decrypt the key from the repository.
- openssl aes-256-cbc -K $encrypted_REPLACE_key -iv $encrypted_REPLACE_iv -in key.json.enc -out key.json -d
# Set up gcloud access to Firebase.
- gcloud auth activate-service-account --key-file=key.json
- gcloud --quiet config set project catsight-be4bc
script:
# Run normal flutter tests.
- "./flutter/bin/flutter test"
# Build e2e tests for android.
- pushd android
- ../flutter/bin/flutter build apk --profile # Profile mode, otherwise keys for signing are necessary.
- ./gradlew app:assembleAndroidTest
- ./gradlew app:assembleDebug -Ptarget=test/cat_sight_e2e.dart
- popd
# Run e2e tests on Firebase test lab
- gcloud firebase test android run --type instrumentation   --app build/app/outputs/apk/debug/app-debug.apk   --test
  build/app/outputs/apk/androidTest/debug/app-debug-androidTest.apk  --timeout 2m
cache:
  directories:
  - $HOME/.pub-cache
  - $HOME/google-cloud-sdk/
  - $HOME/.gradle/caches/
  - $HOME/.gradle/wrapper/
  - $HOME/.android/build-cache
```

And there you have it! Every run of Travis CI will now also include your integration tests.
