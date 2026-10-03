import React, { useEffect, useRef, useState } from 'react';

export default function AnimatedCounter({ value, duration = 800 }) {
  const target = Number(value) || 0;
  const [displayValue, setDisplayValue] = useState(0);
  const previousValue = useRef(0);

  useEffect(() => {
    const startValue = previousValue.current;
    const difference = target - startValue;

    if (difference === 0) {
      setDisplayValue(target);
      return;
    }

    let animationFrame;
    const startTime = performance.now();

    const easeOutCubic = (progress) =>
      1 - Math.pow(1 - progress, 3);

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = easeOutCubic(progress);

      setDisplayValue(
        Math.round(startValue + difference * easedProgress)
      );

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      } else {
        setDisplayValue(target);
        previousValue.current = target;
      }
    };

    animationFrame = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationFrame);
  }, [target, duration]);

  return <>{displayValue}</>;
}
