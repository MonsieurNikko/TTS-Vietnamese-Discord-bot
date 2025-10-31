{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.ffmpeg-full
    pkgs.portaudio
  ];
}
