import React from 'react';

/**
 * Verified Badge Component
 * Displays a blue checkmark icon next to username for verified users
 * Icon and text height are balanced (Instagram/Telegram style)
 */
const VerifiedBadge = ({ isVerified, className = "" }) => {
  if (!isVerified) return null;
  
  return (
    <i 
      className={`fi fi-ss-badge-check ${className}`}
      style={{
        color: '#1DA1F2',
        fontSize: '1em',
        marginLeft: '0.25rem',
        verticalAlign: 'middle',
        lineHeight: '1',
        display: 'inline-block'
      }}
      title="Verified User"
    />
  );
};

export default VerifiedBadge;
