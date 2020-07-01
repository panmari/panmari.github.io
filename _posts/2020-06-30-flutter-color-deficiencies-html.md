---
layout: post
title: Simulating color deficiencies in Flutter
tags: [flutter, graphics, perception, linear-algebra]
---

It's surprisingly easy to create an app that simulates a color deficiency, such as red-green color blindness, by using Flutter's [ColorFiltered](https://www.youtube.com/watch?v=F7Cll22Dno8) widget and applying it to a camera feed.
With this insight as main ingredient, I created an app to simulate the vision of cats, who are red-green color blind. Check it out at the [Google Play](https://play.google.com/store/apps/details?id=ch.panmari.cat_sight) and soon also the Apple app store.

![Screenshot of the app simulating red-green color blindness, i.e. the sight of a cat](/assets/img/screenshot_color_blindness.png)

## Technology & Motivation

I've been meaning to give [Flutter](https://flutter.dev), a framework for cross-platform app development, a try. The dream they're selling almost sounds too good:

> Flutter is Google’s UI toolkit for building beautiful, natively compiled applications for mobile, web, and desktop from a single codebase.

The framework isn't quite there yet. Currently, only Android and iOS are officially supported.

## The theory behind simulating color deficiencies

[Others](https://ixora.io/projects/colorblindness/color-blindness-simulation-research/) have done a very good job at explaining this in detail. Here only the most important bits:

* Humans have three different types of cone cells which roughly correspond to the reception of red, green and blue. Most literature refers to these three types as short, medium and long, or in short S, M and L.
* The cause of red-green color blindness is the lack of L cones.
* Given an RGB input, everything boils down to a bit of linear algebra.

### The math

There's three matrices (in addition with their inverse) involved in the process.

* $$M_{sRGB}$$ - converting RGB to XYZ color space, e.g. from [this reference](http://www.brucelindbloom.com/index.html?Eqn_RGB_to_XYZ.html).
* $$M_{HPE}$$ - converting XYZ to LMS color space using the [Hunt-Pointer-Estevez transformation](https://en.wikipedia.org/wiki/LMS_color_space#Hunt.2C_RLAB) matrix.
* $$S$$ - Applying a color deficiency.

$$
\begin{bmatrix}
   r' \\
   g' \\
   b'
\end{bmatrix}

=

M_{sRGB}^{-1} \cdot
M_{HPE}^{-1} \cdot
S \cdot
M_{HPE} \cdot
M_{sRGB} \cdot
\begin{bmatrix}
   r \\
   g \\
   b
\end{bmatrix}
$$

$$S$$ can be chosen depending on the kind of deficiency you want to simulate. A good starting poing is [this research paper](https://arxiv.org/pdf/1711.10662.pdf) which discusses simulating mixes of deficencies at various strengths. For a given $$S$$, the expression can be simplified since all matrices involved are constant

$$
\begin{bmatrix}
   r' \\
   g' \\
   b'
\end{bmatrix}

=

T_{S} \cdot
\begin{bmatrix}
   r \\
   g \\
   b
\end{bmatrix}
$$

which gives us the matrix $$T_{S}$$ for plugging into the app.

## Implementation

There's two main components here: Getting a camera feed and then applying the color transformation.

### Camera feed

Flutter has thriving plugin environment, many of them provided by the flutter team. The [camera plugin](https://flutter.dev/docs/cookbook/plugins/picture-using-camera) is one of them.

Initialization is somewhat cumbersome, but the documentation does a good job explaining all the steps. I had some trouble figuring out all steps necessary to make it look right on all devices, but in the end succeeded by making use of [AspectRatio](https://api.flutter.dev/flutter/widgets/AspectRatio-class.html) and [RotatedBox](https://api.flutter.dev/flutter/widgets/RotatedBox-class.html).

```dart
class CameraPreviewWidget extends StatefulWidget {
  @override
  CameraPreviewState createState() => CameraPreviewState();
}

class CameraPreviewState extends State<CameraPreviewWidget> {
  CameraController _controller;

  @override
  void initState() {
    super.initState();
    // Initialize _controller.
  }

  @override
  void dispose() {
    // Dispose _controller.
     super.dispose();
 }

  @override
  Widget build(BuildContext context) {
    // Wrapping the CameraPreview in a AspectRatio makes sure the
    // image doesn't distort depending on the screen space available.
    return AspectRatio(
      aspectRatio: _controller.value.aspectRatio,
      // Some sensors are not oriented the same way as the display, thus
      // the camera preview needs to be wrapped in a RotatedBox.
      child: RotatedBox(
        quarterTurns: 1 - _controller.description.sensorOrientation ~/ 90,
        // Camera preview from controller.
        child: CameraPreview(_controller),
      ),
    )
  }
}
```

### Color transformation

So how does the matrix $$T_S$$ from above make it's way to the camera feed? Enter Flutter's [ColorFiltered](https://api.flutter.dev/flutter/widgets/ColorFiltered-class.html) class.

The [introduction video](https://www.youtube.com/watch?v=F7Cll22Dno8) suggests applying it to an image asset in conjunction with blend modes.

![bird going green from introduction video](/assets/img/ColorFiltered_Flutter_Widget_of_the_Week.gif)

But when reading through the docs, I found out that you can also set an arbitrary matrix. Here's a simple example wrapping the widget from above in a `ColorFiltered`.

```dart
Widget build() {
    /*
    From the flutter docs:
    Construct a color filter that transforms a color by a 5x5 matrix, where the fifth row is implicitly added in an identity configuration.

    | R' |   | a00 a01 a02 a03 a04 |   | R |
    | G' |   | a10 a11 a22 a33 a44 |   | G |
    | B' | = | a20 a21 a22 a33 a44 | * | B |
    | A' |   | a30 a31 a22 a33 a44 |   | A |
    | 1  |   |  0   0   0   0   1  |   | 1 |

    */
    // This example switches the red and green color channel.
    const ColorFilter switchRedAndGreen = ColorFilter.matrix([
    0, 1, 0, 0, 0,
    1, 0, 0, 0, 0,
    0, 0, 1, 0, 0,
    0, 0, 0, 0, 0
    ]);
    return ColorFiltered(child: CameraPreviewWidget(), colorFilter: switchRedAndGreen)
}
```

Thanks to Flutter's modular approach, any Widget can go there as a child, also the camera preview described above. A few things to note here:

* Be careful with notation: `ColorFilter` is row-major while Dart's `Matrix4` class is column-major.
* `ColorFilter` is a const and thus needs to be known at compile time. Precompute your matrix!

## Conclusion

Plugging these two things together lead to a quick prototype. Once I was this far, I was already hooked on Flutter. Here's a few things I liked especially:

* Dart is big leap forward from Java, with which I had my last app-writing experience.
* One codebase for all platforms is great!
* The community is fun! For example there's short, easy-to-digest videos that give you an intro to essential components.
* The developer experience is very smooth with nice utilities like the hot reloading, the web debugger and more.

But of course things are not perfect. When polishing [the app](https://play.google.com/store/apps/details?id=ch.panmari.cat_sight) for release, I also encountered a few bumps:

* Some (official!) plugins don't meet the high quality bar of the main components. I ran into several issues when using them.
* At the bottom of all the shiny widgets, there's still bindings to native java/swift/objective-c code. Dealing with issues at this layer is not pretty.
