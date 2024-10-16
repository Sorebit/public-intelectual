CREATE TABLE topic (
    url text PRIMARY KEY,
    title text NOT NULL,
    film_title text NOT NULL,
    film_url text NOT NULL
);

CREATE TABLE comment (
    post_id text PRIMARY KEY,
    topic_url text NOT NULL,  -- TODO: FK to topic
    topic_title text NOT NULL,
    text_content text NOT NULL,
    owner text,  -- NULL znaczy usunięty
    position integer NOT NULL,
    indent integer NOT NULL,
    reply_to_url text,
    reply_to text  -- Jak się nazywa klucz do tej samej tabeli?
);
