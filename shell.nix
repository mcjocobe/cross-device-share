{pkgs, ...}: let
  androidComposition = pkgs.androidenv.composeAndroidPackages {
    toolsVersion = "26.1.1";
    platformToolsVersion = "34.0.5";
    buildToolsVersions = ["34.0.0"];
    platformVersions = ["34"];
    abiVersions = ["arm64-v8a"];
    includeSystemImages = true;
  };
in
  pkgs.mkShell {
    name = "flutter-android-apk-shell";

    buildInputs = [
      pkgs.nodejs_20
      pkgs.jdk17
      pkgs.gradle
      pkgs.flutter
      androidComposition.androidsdk
    ];

    shellHook = ''
      export JAVA_HOME=${pkgs.jdk17}
      export ANDROID_HOME=${androidComposition.androidsdk}/libexec/android-sdk
      export ANDROID_SDK_ROOT=$ANDROID_HOME
      export PATH=$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH
      echo "Environment for APK build is ready."
    '';
  }
