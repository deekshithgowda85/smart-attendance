import React, { useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

const DateRange = () => {
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);

    return (
        <div className="md:col-span-4 space-y-2">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Date range</label>
            <div className="flex items-center gap-2">
                <div className="relative flex-1">
                    <DatePicker
                        className="w-full pl-9 pr-3 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                        placeholderText="Start date"
                        selected={startDate}
                        onChange={(date) => setStartDate(date)}
                        dateFormat="dd/MM/yyyy"
                        isClearable
                        showPopperArrow={false}
                        value={startDate ? startDate : ''}
                    />
                </div>
                <div className="relative flex-1">
                    <DatePicker
                        className="w-full pl-9 pr-3 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                        placeholderText="End date"
                        selected={endDate}
                        onChange={(date) => setEndDate(date)}
                        dateFormat="dd/MM/yyyy"
                        isClearable
                        showPopperArrow={false}
                        value={endDate ? endDate : ''}
                    />
                </div>
            </div>
        </div>
    );
};

export default DateRange;