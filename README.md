
# MARES

This repository contains the application's backend code. The frontend project can be found at:
- [mares-frontend](https://github.com/arizabruno/mares-frontend)


## Intro

The Mares Recommender System is a tool designed for personalizing movie recommendations. It integrates a multidimensional analytical approach to cater to individual viewer preferences.

## Context

The genesis of movie recommendation systems can be traced back to the challenge of navigating an ever-growing repository of cinematic content. With the digital revolution and the advent of streaming services, viewers have been inundated with a plethora of choices. The necessity to filter through this vast sea of content gave birth to the first generation of recommendation systems. As these systems evolved, the complexity of viewer preferences necessitated a more refined approach to recommendation, leading to the development of systems like Mares.

## How it works?

### Step 1: Vectorization of User Preferences

The Mares system begins by converting each of a user's selected favorite movies into comprehensive vectors. These vectors encapsulate a broad spectrum of cinematic attributes, ranging from easily observable features like genre and narrative style to more nuanced characteristics such as thematic elements and directorial nuances. This conversion ensures a rich, multi-dimensional representation of each film, providing a deep insight into the user's cinematic tastes.

### Step 2: Synthesis of the User Interest Vector

Next, the system averages these movie vectors to generate a single 'User Interest Vector'. This vector represents a condensed profile of the user’s preferences, synthesizing their interactions with various film titles into a unified form that can be efficiently analyzed. The vector embodies a holistic view of the user's preferences across multiple cinematic dimensions.

### Step 3: Comparative Analysis via KNN Algorithm

Utilizing the K-nearest neighbors (KNN) algorithm, the Mares system matches the 'User Interest Vector' against a pre-existing database. This database is not just a collection but a structured archive of pre-processed 'User Interest Vectors' for over 160,000 users who have contributed to more than 25 million reviews. Each vector in the database represents the comprehensive cinematic preferences of a user, pre-computed and stored across more than 30 dimensions for accurate matching.

### Step 4: Recommendation Generation

Using the insights gained from the KNN analysis, the system identifies clusters of users whose interests closely align with those of the current user. From this group, the system curates a list of movies that have been highly rated by these similar users. This ensures that the recommendations are personalized, aligning closely with the individual's specific tastes and preferences of similar viewers.


### Simplified Example

<br/>
<br/>

![MARES Diagram](mares-diagram.png)

<br/>
<br/>


The diagram provided is a simplified representation of the process, showcasing it in just two dimensions for clarity and ease of understanding. However, in practice, the Mares system operates in a high-dimensional space, utilizing over 30 dimensions to ensure nuanced and precise personalization.
