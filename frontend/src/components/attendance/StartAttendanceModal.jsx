import React, { useState } from "react";
import RotatingQR from "./RotatingQR";
import { X } from "lucide-react";
import PropTypes from 'prop-types';

export default function StartAttendanceModal({ onClose }) {
  const [showQR, setShowQR] = useState(false);
  // For now, generate a random session ID or timestamp
  const [sessionId] = useState(() => "session-" + Date.now());

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md relative shadow-xl border border-gray-100 animate-in fade-in zoom-in duration-200">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 cursor-pointer"
        >
          <X size={24} />
        </button>

        <h2 className="text-xl font-bold mb-4 text-[var(--text-main)]">Start Attendance</h2>

        {!showQR ? (
          <div className="flex flex-col gap-4">
            <p className="text-[var(--text-body)]">
              Click below to generate a rotating QR code for students to scan.
              This code refreshes every 5 seconds to prevent sharing.
            </p>
            <button
              onClick={() => setShowQR(true)}
              className="w-full py-3 bg-[var(--primary)] text-white rounded-xl hover:bg-[var(--primary-hover)] transition font-medium shadow-md cursor-pointer flex justify-center items-center"
            >
              Generate QR
            </button>
          </div>
        ) : (
          <div className="flex justify-center">
            <RotatingQR
              sessionId={sessionId}
              onClose={onClose}
            />
          </div>
        )}
      </div>
    </div>
  );
}

StartAttendanceModal.propTypes = {
  onClose: PropTypes.func.isRequired,
};
