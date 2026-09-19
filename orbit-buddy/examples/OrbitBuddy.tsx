import LottieView from 'lottie-react-native';
import React, { useCallback, useEffect, useRef } from 'react';
import { View, type ViewStyle } from 'react-native';

export type OrbitBuddyState = 'idle' | 'hello' | 'love';

const SEGMENTS: Record<OrbitBuddyState, readonly [number, number]> = {
  idle: [0, 59],
  hello: [60, 119],
  love: [120, 179],
};

type OrbitBuddyProps = {
  state?: OrbitBuddyState;
  size?: number;
  style?: ViewStyle;
  loopIdle?: boolean;
};

export function OrbitBuddy({
  state = 'idle',
  size = 180,
  style,
  loopIdle = true,
}: OrbitBuddyProps) {
  const animationRef = useRef<LottieView>(null);

  const playState = useCallback(() => {
    const [startFrame, endFrame] = SEGMENTS[state];
    animationRef.current?.play(startFrame, endFrame);
  }, [state]);

  useEffect(() => {
    playState();
  }, [playState]);

  return (
    <View
      accessibilityRole="image"
      accessibilityLabel="Orbit Buddy"
      style={[{ width: size, height: size }, style]}
    >
      <LottieView
        ref={animationRef}
        source={require('../animations/orbit-buddy.json')}
        autoPlay={false}
        loop={false}
        resizeMode="contain"
        onAnimationFinish={() => {
          if (state === 'idle' && loopIdle) {
            playState();
          }
        }}
        style={{ width: size, height: size }}
      />
    </View>
  );
}
