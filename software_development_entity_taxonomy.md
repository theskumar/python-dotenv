# Software Development Entity Type Taxonomy

First-cut taxonomy of software-development-related entity types for tagging, extraction, code review, agent workflows, repo analysis, infrastructure analysis, and documentation analysis.

Total entries: 402

## Product, org, and ownership entities

1. Organization
2. Business unit
3. Engineering team
4. Service owner
5. Code owner
6. Product area
7. Product
8. Application
9. Platform
10. Domain
11. Bounded context
12. Capability
13. Feature
14. Component
15. Module
16. Tool
17. Library
18. SDK
19. Plugin
20. Extension
21. Service catalog entry

## Repository and source-control entities

21. Repository
22. Monorepo
23. Polyrepo
24. Branch
25. Tag
26. Commit
27. Pull request
28. Merge request
29. Code review
30. Diff
31. Patch
32. Release branch
33. Trunk branch
34. Fork
35. Submodule
36. GitHub Action workflow file
37. CODEOWNERS file
38. License file
39. README file
40. Changelog file

## Source-code structure entities

41. Source file
42. Configuration file
43. Build file
44. Script
45. Generated code file
46. Template file
47. Migration file
48. Fixture file
49. Namespace
50. Package
51. Class
52. Interface
53. Struct
54. Enum
55. Function
56. Method
57. Variable
58. Constant
59. Import
60. Call site

## Programming language and runtime entities

61. Programming language
62. Runtime
63. Interpreter
64. Compiler
65. Transpiler
66. Virtual machine
67. Bytecode
68. Standard library module
69. Language server
70. Type checker
71. Package manager
72. Task runner
73. Application framework
74. Web framework
75. Worker runtime
76. Serverless runtime
77. Browser runtime
78. Embedded runtime
79. Polyfill
80. Language toolchain

## Service and API entities

81. Service
82. Microservice
83. Monolith
84. Modular monolith
85. Backend-for-frontend
86. API gateway
87. REST API
88. GraphQL API
89. gRPC service
90. RPC endpoint
91. Webhook
92. Internal API
93. Public API
94. Admin API
95. Health endpoint
96. Readiness endpoint
97. Route
98. Controller
99. Middleware
100. Request handler

## Data and storage service entities

101. Database
102. Relational database
103. NoSQL database
104. Key-value store
105. Document store
106. Columnar database
107. Graph database
108. Time-series database
109. Object storage service
110. File storage service
111. Block storage service
112. Data warehouse
113. Data lake
114. Cache
115. Distributed cache
116. Search index
117. Vector database
118. Blob store
119. Backup store
120. Archive store

## Database schema and query entities

121. Schema
122. Table
123. View
124. Materialized view
125. Column
126. Row
127. Index
128. Primary key
129. Foreign key
130. Constraint
131. Sequence
132. Trigger
133. Stored procedure
134. Query
135. Transaction
136. Migration
137. Seed data
138. Replica
139. Shard
140. Partition

## Messaging, streaming, and integration entities

141. Message queue
142. Topic
143. Subscription
144. Publisher
145. Consumer
146. Producer
147. Event bus
148. Event stream
149. Stream processor
150. Dead-letter queue
151. Retry queue
152. Message broker
153. Kafka cluster
154. Kafka topic
155. RabbitMQ exchange
156. Pub/Sub topic
157. Event schema
158. Integration connector
159. ETL job
160. CDC stream

## Frontend and web entities

161. Web app
162. Single-page app
163. Static site
164. Server-rendered page
165. Frontend component
166. Design system component
167. Route component
168. Page component
169. Form
170. Client-side store
171. Browser cache
172. Service worker
173. Web worker
174. Asset bundle
175. JavaScript chunk
176. CSS module
177. Theme
178. Accessibility landmark
179. Browser API
180. Frontend build artifact

## Mobile, desktop, and client entities

181. Mobile app
182. iOS app
183. Android app
184. Desktop app
185. CLI app
186. Command
187. Subcommand
188. Command-line flag
189. Command-line argument
190. Terminal UI
191. Native module
192. Mobile screen
193. Mobile view model
194. App store build
195. App signing certificate
196. Push notification
197. Deep link
198. Local storage
199. Offline sync module
200. Client SDK

## Build, package, and dependency entities

201. Build system
202. Build target
203. Build artifact
204. Binary artifact
205. Container image artifact
206. Package
207. Dependency
208. Transitive dependency
209. Dev dependency
210. Lockfile
211. Dependency graph
212. Artifact registry
213. Package registry
214. Docker registry
215. Version constraint
216. Semantic version
217. Build cache
218. Build step
219. Build script
220. Release artifact

## Testing and quality entities

221. Test suite
222. Unit test
223. Integration test
224. End-to-end test
225. Contract test
226. Snapshot test
227. Load test
228. Stress test
229. Smoke test
230. Regression test
231. Test fixture
232. Mock
233. Stub
234. Fake
235. Test harness
236. Coverage report
237. Static analysis rule
238. Lint rule
239. Code quality gate
240. Mutation test

## CI/CD and release entities

241. CI pipeline
242. CD pipeline
243. Workflow
244. Job
245. Step
246. Runner
247. Build matrix
248. Pipeline trigger
249. Required check
250. Deployment gate
251. Approval step
252. Release
253. Release candidate
254. Deployment
255. Rollout
256. Rollback
257. Canary release
258. Blue-green deployment
259. Feature flag rollout
260. Release notes

## Containers and Kubernetes entities

261. Container
262. Container image
263. Dockerfile
264. Docker Compose service
265. Kubernetes cluster
266. Kubernetes namespace
267. Pod
268. Deployment
269. StatefulSet
270. DaemonSet
271. ReplicaSet
272. Job
273. CronJob
274. Service
275. Ingress
276. ConfigMap
277. Secret
278. PersistentVolume
279. PersistentVolumeClaim
280. Helm chart

## Infrastructure and networking entities

281. Environment
282. Region
283. Availability zone
284. Data center
285. Virtual machine
286. Bare-metal host
287. Load balancer
288. Reverse proxy
289. Forward proxy
290. DNS zone
291. DNS record
292. CDN
293. VPC
294. Subnet
295. Route table
296. NAT gateway
297. Internet gateway
298. Firewall rule
299. Security group
300. Network policy

## Cloud and AWS entities

301. Cloud account
302. Cloud organization
303. IAM user
304. IAM role
305. IAM policy
306. IAM group
307. AWS account
308. AWS Organization
309. AWS IAM role
310. AWS Lambda function
311. AWS ECS service
312. AWS EKS cluster
313. AWS EC2 instance
314. AWS S3 bucket
315. AWS RDS instance
316. AWS DynamoDB table
317. AWS SQS queue
318. AWS SNS topic
319. AWS CloudFormation stack
320. AWS CloudWatch alarm

## Infrastructure-as-code and configuration entities

321. Infrastructure-as-code module
322. Terraform module
323. Terraform resource
324. Terraform provider
325. Terraform variable
326. Terraform output
327. Terraform state
328. CloudFormation template
329. Pulumi stack
330. Ansible playbook
331. Ansible role
332. Chef cookbook
333. Puppet manifest
334. Helm values file
335. Kustomize overlay
336. Environment variable
337. Configuration key
338. Configuration profile
339. Secrets configuration
340. Policy-as-code rule

## Security, identity, and compliance entities

341. User account
342. Service account
343. Machine identity
344. API key
345. Access token
346. Refresh token
347. OAuth client
348. OIDC provider
349. SAML provider
350. Certificate
351. Private key
352. Public key
353. Secret
354. Secret manager entry
355. Vulnerability
356. CVE
357. Security finding
358. Compliance control
359. Audit log
360. Threat model

## Observability and operations entities

361. Log
362. Log stream
363. Metric
364. Counter metric
365. Gauge metric
366. Histogram metric
367. Trace
368. Span
369. Dashboard
370. Alert
371. SLO
372. SLA
373. SLI
374. Error budget
375. Incident
376. Postmortem
377. Runbook
378. On-call rotation
379. Pager escalation
380. Operational playbook

## Architecture, ML, docs, and workflow entities

381. Architecture diagram
382. Sequence diagram
383. Dependency diagram
384. Data-flow diagram
385. ADR
386. Design doc
387. RFC
388. Technical specification
389. User story
390. Bug report
391. Task
392. Epic
393. Roadmap item
394. ML model
395. Training job
396. Feature store
397. Dataset
398. Model endpoint
399. Experiment
400. Notebook
401. Skill
