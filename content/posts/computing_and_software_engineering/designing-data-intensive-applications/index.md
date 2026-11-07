---
title: "Designing Data-Intensive Applications by Martin Kleppmann"
author: "Martin Kleppmann"
authors: ["Martin Kleppmann"]
categories: ["Computing and Software Engineering"]
description: "A guide to the trade-offs behind reliable data systems, from storage and replication to transactions, consensus, and stream processing."
image: "image.png"
---

# How Data Systems Keep Their Promises

A database can accept a write while a search index misses it. A retry can count the same purchase twice. A server can appear dead when its network is merely slow. These problems connect the subjects in Martin Kleppmann's *Designing Data-Intensive Applications*.

The central argument is that sound architecture requires an understanding of mechanisms, guarantees, and trade-offs. Product names alone tell us little. Engineers need to know what a system promises, what assumptions support that promise, and what happens when those assumptions fail. The [author's introduction](https://martin.kleppmann.com/2017/03/27/designing-data-intensive-applications.html) presents this comparison of underlying ideas as the book's purpose.

This summary covers the 2017 first edition, written by Kleppmann alone. Its three parts move from the foundations of data systems to distributed data and then derived data. The examples below simplify the mechanisms to explain their practical consequences.

## Start with Reliability, Scalability, and Maintainability

Kleppmann gives system design three broad goals. **Reliability** means continuing to work correctly despite faults. A broken disk is a fault; losing the service's ability to meet its requirements is a failure. Good design prevents expected faults from becoming failures.

**Scalability** concerns how a system handles growth. First describe the load. Requests per second, data volume, and the distribution of activity can expose different limits. Then measure performance under that load. An average response time can hide the slow requests that cause users difficulty.

**Maintainability** includes operating the system, understanding it, and changing it. A design that needs constant expert intervention has a real cost, even if its benchmark looks good. These goals, developed in [the opening chapter](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/ch01.html), make operational work part of architecture.

## Choose Data Models Around Relationships

The book compares relational, document, and graph models. Each makes some relationships easier to express.

A document can keep a self-contained record together. A relational model can represent shared entities without copying their details everywhere. A graph model makes connections central to queries. Consider a professional network: a profile, its employment history, and paths between connected people present different modeling needs.

The question is how the data will be read and changed. Duplicating an organization name inside many records may simplify a read. Renaming that organization then requires many updates. Normalization reduces this duplication but can require joins.

Declarative query languages add another useful separation. The application states the result it needs, while the database chooses an execution plan. Kleppmann's [data-model discussion](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/ch02.html) encourages readers to examine these consequences before choosing a database family.

## Storage Engines Move Costs Between Operations

An index speeds up selected reads by maintaining an additional structure. That structure consumes space and adds work to writes. Every index therefore supports some access patterns at a cost.

Kleppmann compares B-trees with log-structured storage, including LSM-trees. B-trees organize data in pages and update those pages. LSM-based designs buffer writes and merge sorted data files over time. Their background merging, called compaction, creates additional work. Neither structure wins for every workload.

The distinction between transactions and analytics is equally important. Looking up one order differs from calculating sales across a large history. Column-oriented storage can help analytical scans by reading the relevant columns and compressing similar values together. The [storage chapter](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/ch03.html) connects internal structures to these workload choices. Its practical lesson is to investigate the work an engine performs, then measure it with representative data.

## Design for Old and New Software to Coexist

Data often outlives the code that created it. During a rolling deployment, old and new services may run together. Stored records may remain for years.

Kleppmann examines encoding formats and schema evolution through compatibility. Backward compatibility lets new code read old data. Forward compatibility lets old code read data produced by new code, within defined limits. Adding an optional field with a sensible default can be easier than changing the meaning of an existing field.

A database that does not enforce a schema still has expectations in application code. Those expectations need management. The [encoding and evolution chapter](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/ch04.html) treats compatibility as a requirement across databases, service calls, and messages.

## Replication and Partitioning Solve Different Problems

**Replication** keeps copies of the same data on several machines. It can improve availability, reduce geographic distance, and increase read capacity. Its difficult part is coordinating changes.

With asynchronous leader-based replication, a leader can acknowledge a write before a follower receives it. A user who updates a profile and then reads from that follower may see the old profile. Reading one's own writes is a specific guarantee that addresses this experience. Synchronous replication waits for acknowledgment from participating replicas, adding delay and dependence on their availability. Multi-leader and leaderless approaches introduce further questions about conflicting writes. These trade-offs are developed in [the replication chapter](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/ch05.html).

**Partitioning**, also called sharding, divides a dataset into pieces. Different machines can store and process different pieces. Range partitioning preserves useful ordering but can concentrate traffic. Hash partitioning can spread keys more evenly, while making range queries harder. A single popular key can still create a hot spot.

Replication and partitioning often work together: each partition has several replicas. The extra capacity comes with routing, rebalancing, and cross-partition coordination costs, as [the partitioning chapter](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/ch06.html) explains.

## Transactions Define What Concurrent Work Can Observe

Transactions help applications handle partial updates and concurrent access. However, the label “ACID” does not fully specify behavior. Isolation levels differ, and their names can hide differences between implementations.

Consider two people editing the same record. Both read its original value, then each writes a replacement. Without suitable protection, one change can overwrite the other. Other anomalies involve transactions that update different records while jointly breaking a rule.

**Serializability** means committed transactions have an effect equivalent to running them one at a time in some order. Systems can achieve it through serial execution, locking, or techniques that detect conflicts and abort transactions. Applications must handle retries correctly. Kleppmann's [transaction chapter](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/ch07.html) and his [Hermitage isolation tests](https://martin.kleppmann.com/2014/11/25/hermitage-testing-the-i-in-acid.html) support a precise approach: name the anomaly that must be prevented, then verify the chosen guarantee.

## Distributed Systems Must Act Under Uncertainty

A timeout cannot tell us exactly what happened. A request may have been lost. The server may have completed it and lost the reply. The server may still be working.

Clocks can disagree, processes can pause, and networks can delay messages. These are normal design conditions in [the distributed-systems discussion](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/ch08.html). Treating a timeout as proof that an operation failed can make a retry unsafe.

The next step is to define stronger abstractions. **Linearizability** makes operations appear to act on one current copy of the data, respecting real-time order. It differs from serializability, which concerns transactions and their possible serial order.

Consensus allows nodes to agree on decisions, such as an ordered sequence of operations. It supports coordination despite failures, under stated assumptions. It cannot promise progress through every loss of communication. The [consistency and consensus chapter](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/ch09.html) explains the value and cost of these guarantees.

Kleppmann also rejects using CAP as a vague “pick two” slogan. During a network partition, linearizability conflicts with the theorem's requirement that every request to a non-failing node receive a successful response. His [CAP explanation](https://martin.kleppmann.com/2015/05/11/please-stop-calling-databases-cp-or-ap.html) shows why actual operations and configurations need closer examination.

## Derived Data Connects Databases, Batches, and Streams

An application may need a database, a search index, and an analytical store. Kleppmann distinguishes authoritative records from **derived data**, which can be reconstructed from other data.

Batch processing transforms a bounded input into an output. Its predictable inputs make reprocessing useful: correct a transformation and rebuild the result. Stream processing handles events that continue arriving. It must also account for late events, ordering, and recovery.

Logs connect these ideas. A retained sequence of changes can feed multiple consumers. Change data capture exposes database changes so other systems can maintain derived views. This avoids relying on an application to make two independent writes succeed together. The author's related report, [*Making Sense of Stream Processing*](https://martin.kleppmann.com/papers/stream-processing.pdf), explains this integration model.

Recovery still requires care. Replaying an event must not apply a business effect twice. An idempotent operation has the same effect when repeated. Deduplication and atomic updates can also help, within their supported boundaries. The [stream-processing chapter](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/ch11.html) makes fault tolerance part of data processing rather than an afterthought.

## Practical Implications and Limits

My practical reading is to begin a design review with promises: which records are authoritative, how stale a read may be, which rules must always hold, and what a retry can repeat. Then ask how the team will detect errors and rebuild damaged results. These questions turn broad goals into testable requirements.

The book's final chapter also examines privacy, tracking, and predictive analytics. Technical correctness does not settle whether collecting or using data serves people well. Kleppmann explicitly presents [his future-system proposals](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/ch12.html) as opinions for discussion.

The book provides conceptual depth rather than deployment instructions. Its first-edition product examples describe their period; they should not establish the capabilities of a current release. Readers must check current documentation and test their own configurations. Understanding the theory also does not remove the need for backups, monitoring, recovery practice, or judgment about operational complexity.

Its lasting contribution is a method of asking better questions. A useful architecture makes its assumptions visible and chooses guarantees that fit the consequences of being wrong.

## Sources

- [Martin Kleppmann: first-edition publication record and purpose](https://martin.kleppmann.com/2017/03/27/designing-data-intensive-applications.html).
- [O'Reilly: first-edition title, author, and contents](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/titlepage01.html), with chapter previews linked throughout this summary.
- [Kleppmann: Hermitage transaction-isolation tests](https://martin.kleppmann.com/2014/11/25/hermitage-testing-the-i-in-acid.html), a supporting explanation of isolation differences.
- [Kleppmann: CAP and linearizability](https://martin.kleppmann.com/2015/05/11/please-stop-calling-databases-cp-or-ap.html), a supporting technical explanation.
- [Kleppmann: *Making Sense of Stream Processing*](https://martin.kleppmann.com/papers/stream-processing.pdf), a separate, related report on logs and data integration.
