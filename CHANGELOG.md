# Changelog

## [1.7.0](https://github.com/allisson/fastqueue/compare/v1.6.0...v1.7.0) (2023-04-26)


### Features

* add an endpoint for health check ([#50](https://github.com/allisson/fastqueue/issues/50)) ([fd102bc](https://github.com/allisson/fastqueue/commit/fd102bc3bd2bd68d01cd95d4479f67b654ce61bd))
* upgrade sqlalchemy to version 2.x ([#48](https://github.com/allisson/fastqueue/issues/48)) ([2f74302](https://github.com/allisson/fastqueue/commit/2f74302d683068a2dda347d35d356b68d2d26a6c))

## [1.6.0](https://github.com/allisson/fastqueue/compare/v1.5.0...v1.6.0) (2023-03-16)


### Features

* pin dependencies on major version ([#46](https://github.com/allisson/fastqueue/issues/46)) ([289baf4](https://github.com/allisson/fastqueue/commit/289baf4a3d0a921564114b4632d8ffcc6e96b94e))

## [1.5.0](https://github.com/allisson/fastqueue/compare/v1.4.0...v1.5.0) (2023-01-11)


### Features

* convert services to be used as instances ([#44](https://github.com/allisson/fastqueue/issues/44)) ([8e95aea](https://github.com/allisson/fastqueue/commit/8e95aea14f924ac3d46f37ea8a55c461e60d7126))

## [1.4.0](https://github.com/allisson/fastqueue/compare/v1.3.2...v1.4.0) (2022-11-19)


### Features

* add delay queues support ([#41](https://github.com/allisson/fastqueue/issues/41)) ([62b5db6](https://github.com/allisson/fastqueue/commit/62b5db6f60d3bfc0c2baee81903883bdebab80ce))

## [1.3.2](https://github.com/allisson/fastqueue/compare/v1.3.1...v1.3.2) (2022-10-25)


### Bug Fixes

* revert to psycopg2-binary ([#39](https://github.com/allisson/fastqueue/issues/39)) ([662b199](https://github.com/allisson/fastqueue/commit/662b199d17da691ee44d320007bac78841cfd175))

## [1.3.1](https://github.com/allisson/fastqueue/compare/v1.3.0...v1.3.1) (2022-10-25)


### Bug Fixes

* replace psycopg2-binary with psycopg2 ([#37](https://github.com/allisson/fastqueue/issues/37)) ([056323f](https://github.com/allisson/fastqueue/commit/056323f54d510148bd02b206e2604743b1837b91))

## [1.3.0](https://github.com/allisson/fastqueue/compare/v1.2.0...v1.3.0) (2022-10-25)


### Features

* use python 3.11 ([#35](https://github.com/allisson/fastqueue/issues/35)) ([162078d](https://github.com/allisson/fastqueue/commit/162078d8eb1f6ce7b9f63197ef432ca077399162))

## [1.2.0](https://github.com/allisson/fastqueue/compare/v1.1.0...v1.2.0) (2022-10-14)


### Features

* add prometheus metrics support ([#33](https://github.com/allisson/fastqueue/issues/33)) ([a624be1](https://github.com/allisson/fastqueue/commit/a624be14b84b88120239ee13a3fd518d048b749e))

## [1.1.0](https://github.com/allisson/fastqueue/compare/v1.0.0...v1.1.0) (2022-10-07)


### Features

* add redrive support ([#31](https://github.com/allisson/fastqueue/issues/31)) ([3eac767](https://github.com/allisson/fastqueue/commit/3eac7678b883df409eb3dbcc9bd63f7ac82e175b))

## 1.0.0 (2022-10-06)


### Features

* add ack and nack endpoints ([#13](https://github.com/allisson/fastqueue/issues/13)) ([940a5c6](https://github.com/allisson/fastqueue/commit/940a5c698136d2ff94f2f0735e113d01a5657378))
* add base models ([#4](https://github.com/allisson/fastqueue/issues/4)) ([f47cf1c](https://github.com/allisson/fastqueue/commit/f47cf1cea200eb54a6c631f8bcf1c1738942d2e1))
* add basic fastapi setup ([#2](https://github.com/allisson/fastqueue/issues/2)) ([12e71a5](https://github.com/allisson/fastqueue/commit/12e71a5c730d6cc64d842ef10c5b7a5d7f9e06b7))
* add database echo support ([#26](https://github.com/allisson/fastqueue/issues/26)) ([15b383f](https://github.com/allisson/fastqueue/commit/15b383fb68c8c350ab2f08e4264c5fafad484cbd))
* add database migrations with alembic ([#3](https://github.com/allisson/fastqueue/issues/3)) ([4bb4ae5](https://github.com/allisson/fastqueue/commit/4bb4ae5376b2af521e72cdd3e6cf7d1fc2a97dd6))
* add dead queue support ([#18](https://github.com/allisson/fastqueue/issues/18)) ([8e32aa0](https://github.com/allisson/fastqueue/commit/8e32aa0cd78d9a55d271c0af8e4e17cd3e77e7d2))
* add endpoint to purge the queue messages ([#22](https://github.com/allisson/fastqueue/issues/22)) ([b55c7fd](https://github.com/allisson/fastqueue/commit/b55c7fdca1efeef3ea702991d7a7782b1944c755))
* add MessageService ([#9](https://github.com/allisson/fastqueue/issues/9)) ([bf328bf](https://github.com/allisson/fastqueue/commit/bf328bfa80a86b9ff6730facf50631858ccd6105))
* add MessageService.list_for_consume ([#10](https://github.com/allisson/fastqueue/issues/10)) ([901bd1b](https://github.com/allisson/fastqueue/commit/901bd1b443b7008d273ea2fcfc4aed90746584d7))
* add queue stats endpoint ([#14](https://github.com/allisson/fastqueue/issues/14)) ([76c906a](https://github.com/allisson/fastqueue/commit/76c906a3c8ef3afeff2a57672ae8ec40c63aa487))
* add queues and messages endpoints ([#12](https://github.com/allisson/fastqueue/issues/12)) ([be80f17](https://github.com/allisson/fastqueue/commit/be80f17327cc4c9e318601a442f02d8bf9083fce))
* add QueueService ([#8](https://github.com/allisson/fastqueue/issues/8)) ([29c9768](https://github.com/allisson/fastqueue/commit/29c9768ceb87b5e59ee7f6fda5ab51373973fee5))
* add QueueService cleanup method ([#16](https://github.com/allisson/fastqueue/issues/16)) ([f15f30a](https://github.com/allisson/fastqueue/commit/f15f30a41ea33fa737addcbd522d88fea0954c73))
* add topics endpoints ([#11](https://github.com/allisson/fastqueue/issues/11)) ([f8dd58a](https://github.com/allisson/fastqueue/commit/f8dd58a21b8b3add74686cc54850b82778d17b40))
* add TopicService ([#7](https://github.com/allisson/fastqueue/issues/7)) ([08ccad7](https://github.com/allisson/fastqueue/commit/08ccad7b3adc8a4e506177ea83ab775dc38aec48))
* add worker entrypoint ([#17](https://github.com/allisson/fastqueue/issues/17)) ([6627950](https://github.com/allisson/fastqueue/commit/662795060da39e0b15f1bd8fbe188d7c6c43a82f))
* configure the base setup on github ([#1](https://github.com/allisson/fastqueue/issues/1)) ([803b70c](https://github.com/allisson/fastqueue/commit/803b70c78c7fa4b0e4fda2576c0b660d8ddf748d))
* update env.sample ([#21](https://github.com/allisson/fastqueue/issues/21)) ([7bce9a2](https://github.com/allisson/fastqueue/commit/7bce9a2c7d32e4bbb7e1c1943d1a612adbbcf6cc))
* update readme with basic quickstart ([#23](https://github.com/allisson/fastqueue/issues/23)) ([741264e](https://github.com/allisson/fastqueue/commit/741264ebffac2e71bd13683a5ee815bed7e71d58))
* use only sqlalchemy for orm ([#5](https://github.com/allisson/fastqueue/issues/5)) ([fe1fc44](https://github.com/allisson/fastqueue/commit/fe1fc4456398c2d1c6d3435d6aebc3a0887da386))


### Bug Fixes

* fix dockerfile ([#15](https://github.com/allisson/fastqueue/issues/15)) ([df7a988](https://github.com/allisson/fastqueue/commit/df7a9880d5fef0a78a79776f7ef84c7ff953bfea))
* make message_max_deliveries required for dead_queue_id ([#19](https://github.com/allisson/fastqueue/issues/19)) ([9c31692](https://github.com/allisson/fastqueue/commit/9c316921708d41b5be8a203ae3af04fc6a2f9a49))
