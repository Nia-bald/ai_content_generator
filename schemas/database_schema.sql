CREATE TABLE OpInfo (
    OpInfoId INT PRIMARY KEY,
    OpName VARCHAR(255),
    OpFollowers INT
);

CREATE TABLE EngagmentTable (
    EngagmentTableId INT PRIMARY KEY,
    UpvoteCount INT,
    DownvoteCount INT,
    DateOfPosting DATE,
    ViewCount INT,
    Comments TEXT
);

CREATE TABLE PostProductionTable (
    PostProductionTableId INT PRIMARY KEY,
    ChannelId VARCHAR(255),
    Tags TEXT,
    Description TEXT,
    Credit TEXT,
    Title VARCHAR(255),
    Rank INT,
    RankingAlgorithm VARCHAR(255),
    MediaPath TEXT,
    DateOfPosting DATE,
    ViewCount INT,
    Likes INT,
    YouTubeAnalytics JSON  -- You can replace this with specific columns if structured
);

CREATE TABLE RedditPostTable (
    PostId INT PRIMARY KEY,
    Content TEXT,
    Type VARCHAR(100),
    MediaPath TEXT,
    SubredditName VARCHAR(255),
    Rank INT,
    RankingAlgorithm VARCHAR(255),
    EngagmentTableId INT,
    OpInfoId INT,
    PostProductionTableId INT,
    FOREIGN KEY (EngagmentTableId) REFERENCES EngagmentTable(EngagmentTableId),
    FOREIGN KEY (OpInfoId) REFERENCES OpInfo(OpInfoId),
    FOREIGN KEY (PostProductionTableId) REFERENCES PostProductionTable(PostProductionTableId)
);

CREATE TABLE VideoTable (
    VideoId INT PRIMARY KEY,
    UpvoteCount INT,
    DownvoteCount INT,
    DateOfPosting DATE,
    ViewCount INT,
    Comments TEXT,
    Type VARCHAR(100),
    VideoPath TEXT,
    MediaPath TEXT
);
