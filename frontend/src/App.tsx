import React, { useEffect, useState } from "react";
import { fetchEvents } from "./api";
import { EventData } from "./types";
import ResultsTable from "./components/ResultsTable";
import Filters from "./components/Filters";

const App: React.FC = () => {
    const [events, setEvents] = useState<EventData[]>([]);
    const [sport, setSport] = useState<string>("");
    const [keyword, setKeyword] = useState<string>("");
    const [hours, setHours] = useState<number>(24);

    const loadEvents = async () => {
        try {
            const data = await fetchEvents({ sport, keyword, hours });
            setEvents(data);
        } catch (error) {
            console.error("Error fetching events:", error);
        }
    };

    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => {
        loadEvents();
    }, [sport, keyword, hours]);

    return (
        <div style={{ padding: "20px" }}>
            <h1>Results</h1>
            <Filters
                sport={sport}
                keyword={keyword}
                hours={hours}
                onSportChange={setSport}
                onKeywordChange={setKeyword}
                onHoursChange={setHours}
            />
            <ResultsTable events={events} />
        </div>
    );
};

export default App;