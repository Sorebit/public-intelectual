CREATE TABLE comment (
    post_id text PRIMARY KEY,
    topic_url text NOT NULL,
    text_content text NOT NULL,
    owner text,
    position integer NOT NULL,
    indent integer NOT NULL,
    reply_to text
);
