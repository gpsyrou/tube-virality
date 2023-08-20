# Tube Virality Project
![Python](https://img.shields.io/badge/-Python-000?&logo=Python)
![Go](https://img.shields.io/badge/-Golang-000?&logo=go)

## YouTube Trending Video Analytics API

**Purpose:** The **Tube Virality** project aims to develop a comprehensive API that retrieves metadata, including view counts, likes, and descriptions, from YouTube videos and channels. Unlike relying on existing APIs, we're creating this retrieval API from the ground up. This approach grants us full control over all levels of abstraction, ensuring our API's efficiency and flexibility.

We will not only gather data but also utilize the API to collect information about a curated selection of trending YouTube videos over time. Once a substantial dataset is collected, we'll proceed to the next phase: analyzing the collected data to uncover insights and answer critical questions:

- What factors contribute to a YouTube video going viral?
- Can we construct a model capable of predicting when a new video has the potential to go viral?

## About the Project

The **Tube Virality** project is dedicated to constructing an API tailored to fetch statistics and details related to trending YouTube videos. Moreover, we're committed to conducting descriptive statistical analyses and crafting predictive models that gauge the likelihood of a trending video attaining viral status.

### Refining Ideas for YouTube Virality Project

#### Defining Virality with Custom Logic

Determining the factors that contribute to a video's virality will necessitate a tailored approach. For instance, a video from a renowned YouTuber might garner 20 million views despite having only 1 million subscribers. Conversely, a video from a YouTuber with 10,000 subscribers could amass 2 million views, representing a more substantial and intriguing impact. Crafting a "success-story" criterion will require the establishment of guidelines to define virality thresholds.

#### Data Gathering as the First Step

The path to accomplishing the aforementioned objectives commences with data collection. We will initiate by collating daily trending videos in the UK, coupled with their respective trending positions for each date. This methodological selection will enable us to assemble a representative assortment of captivating YouTube videos. Subsequently, guided by the principles outlined in the custom virality logic, we will categorize the dataset into two distinct segments: "success" and "non-success" stories, leading to a form of supervised labeling.


## Technologies Utilized

We've harnessed a blend of cutting-edge technologies to power the **Tube Virality** project:

- **Python 3.9:** This versatile programming language is at the core of our project, facilitating data manipulation, analysis, and model development.
- **SQL:** We're leveraging SQL databases to efficiently store and manage the collected data, ensuring scalability and structured data retrieval.
- **Go:** With the power of Go, we're enhancing our API's performance and concurrent processing capabilities, resulting in a robust and responsive user experience.

## Installation

WIP

## Usage

WIP

* temporary pull trending `make runPullTrending`
* temporary run `make run2video`

## Contributors

- [Georgios Spyrou](https://github.com/gpsyrou)

## License

This project is licensed under the [MIT License](LICENSE).


### Proposed High-Level Architecture

```mermaid
graph TD;

subgraph YouTube Data Collection
    A1[Collect Trending Videos for a Specific Day] --> A2[Generate List of Trending Video URLs]
    A2 --> B{Video Metadata Collector}
    B --> C[Video Metadata: Views, Likes, Description, Comments]
    B --> D{Channel Metadata Collector}
    D --> E[Channel Metadata: User, Subscribers]
end

subgraph Data Storage
    F[SQL Database]
    C --> F
    E --> F
end

subgraph Data Analytics & Machine Learning
    G[Data Analysis & Visualization]
    H[Custom Logic for Virality]
    I[Supervised Learning Models]
    G --> H
    G --> I
    F --> H
    F --> I
    H --> J[Virality Prediction]
end

```

### Entity-Relatioship Diagram for Data Storage Module

<p align="center">
  <img src="/assets/img/ERD_youtube.png" width="720" title="hover text">
</p>
