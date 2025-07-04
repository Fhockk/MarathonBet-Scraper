import React from "react";

interface Props {
    sport: string;
    keyword: string;
    hours: number;
    onSportChange: (s: string) => void;
    onKeywordChange: (k: string) => void;
    onHoursChange: (h: number) => void;
}

const Filters: React.FC<Props> = ({
        sport,
        keyword,
        hours,
        onSportChange,
        onKeywordChange,
        onHoursChange,
    }) => {
    return (
        <div style={{ marginBottom: 20 }}>
            <input
                placeholder="Sport"
                value={sport}
                onChange={(e) => onSportChange(e.target.value)}
                style={{ marginRight: 10 }}
            />
            <input
                placeholder="Keyword"
                value={keyword}
                onChange={(e) => onKeywordChange(e.target.value)}
                style={{ marginRight: 10 }}
            />
            <input
                type="number"
                placeholder="Hours"
                value={hours}
                onChange={(e) => onHoursChange(Number(e.target.value))}
            />
        </div>
    );
};

export default Filters;
