# Feature Store Notes

![diagram](images/diagram.png)

- [What is a Feature Store in ML, and Do I Need One?](https://www.qwak.com/post/what-is-a-feature-store-in-ml)

- [Feature Store - MadewithML](https://madewithml.com/courses/mlops/feature-store/#when-do-i-need-a-feature-store)
    - [repo link](https://github.com/GokuMohandas/feature-store/tree/main)

- [Feature Store : Definitve Guide - Hopworks-blog](https://mljam.com/feature-store/)


**Feature Store in Inference API**


```mermaid
flowchart TB
    R["API Request"] --> P["Prediction Service"]
    OF["Online Features (Redis)"] --> P
    P --> PR["Prediction"]
    P --> OF
    OF --> BS["Batch Storage (PostgreSQL)"]

```
