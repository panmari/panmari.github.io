---
layout: post
title: Blur the background of a flutter app with a cutout
tags: [flutter, blur, highlight]
---

Every once in a while you want to draw the attention of a user to a specific part of your app. One way of doing so is blurring all screen content, except a small cutout.

<img src="/assets/img/blur_cutout_before.png" width="40%"/> <img src="/assets/img/blur_cutout_after.png" width="40%"/> 

The general idea how to achieve this in flutter is

1. Create a stack with two items
    1. The app content
    1. A `BackdropFilter` using `ImageFilter.blur`
1. Create a cutout using a `CustomPaint`

But let's take it slow and go step by step.

## Blur content using a stack and a backdrop filter

This is pretty straight forward. Wrap your existing content in a stack with 2 items: your content and a [`BackdropFilter`](https://api.flutter.dev/flutter/widgets/BackdropFilter-class.html). The child of the `BackdropFilter` decides on the region the filter is applied. The example below uses a container that takes up all available space.

```dart
class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[200],
      body: Stack(
        children: [
          YourHomeScreenContent(),
          // This is where the blurring happens
          BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 3, sigmaY: 3),
            // A container that expands to the full available space.
            child: Container(
              alignment: Alignment.center,
              color: Colors.transparent,
            ),
          ),
        ],
      ),
    );
  }
}
```

## Create a cutout to the blur area

To create a cutout, add a `CustomPaint` child to the container defining the blur area.

```dart
          BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 3, sigmaY: 3),
            child: Container(
              alignment: Alignment.center,
              // Choose Colors.black here if you want a shadow effect in addition to blurring.
              color: Colors.transparent,
              // This part is new, creating the cutout.
              child: CustomPaint(
                  size: size,
                  painter: Hole(),
              ),
            ),
          ),
```

Here's an example implementation for creating a circular hole. `CustomPainter` also supports much more advanced shapes (and combination of shapes!) so make sure to read up on the [documentation](https://api.flutter.dev/flutter/rendering/CustomPainter-class.html).

```dart
/// [Hole] provides a custom painter for leaving a circular hole with some
/// fuziness.
class Hole extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    double radius = 100;
    double blurRadius = 10;
    canvas.drawCircle(
      Offset(0, -100),
      radius,
      Paint()
        ..blendMode = BlendMode.xor
        // The mask filter gives some fuziness to the cutout.
        ..maskFilter = MaskFilter.blur(BlurStyle.normal, blurRadius),
    );
  }

  @override
  bool shouldRepaint(Hole oldDelegate) => false;
}
```
