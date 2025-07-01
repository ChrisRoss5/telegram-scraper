interface Reaction {
  reaction: string;
  count: number;
}

interface ForwardInfo {
  from_name?: string;
  username?: string;
  id?: number;
}

interface MediaItem {
  media_type: string;
  media_path: string;
}

interface Poll {
  question: string;
  answers: string[];
  results: number[];
  total_voters: number;
}

interface TelegramMessage {
  id: number;
  date: string; // "DD.MM.YYYY. HH:MM:SS" format
  is_forwarded?: boolean;
  forward?: ForwardInfo;
  reply_to?: number;
  sender_id?: number;
  first_name?: string;
  last_name?: string;
  username?: string;
  message?: string;
  reactions?: Reaction[];
  views?: number; // only for non-comment messages
  forwards?: number; // only for non-comment messages
  media?: MediaItem[];
  poll?: Poll;
  comments?: TelegramMessage[]; // only for root messages
}
