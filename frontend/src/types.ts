export interface EventMetadata {
    competition_id: number;
    competition_name: string;
    home_team: string;
    away_team: string;
    start_time: number;
    extra?: Record<string, any>
}

interface Score {
    label?: string;
    value: string;
}

export interface EventState {
    is_live?: boolean
    scores: { value: string; label?: string }[];
}

export interface Event {
    event_id: string
    sport: string
    metadata: EventMetadata
    state: EventState
    extra?: Record<string, any>
}

export interface EventData {
    event_id: number;
    sport: string;
    metadata: {
        competition_name: string;
        home_team: string;
        away_team: string;
        start_time: number;
    };
    state?: {
        scores: { value: string; label?: string }[];
    };
}

