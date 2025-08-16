# 📦 Repo2MD Export: who-am-ai

## 📂 프로젝트 트리
```
who-am-ai/
    ├── gradle/
    │   └── wrapper/
    │       ├── gradle-wrapper.jar
    │       └── gradle-wrapper.properties
    ├── src/
    │   ├── main/
    │   │   ├── kotlin/
    │   │   │   └── com/
    │   │   │       └── dd3ok/
    │   │   │           └── whoamai/
    │   │   │               ├── adapter/
    │   │   │               │   ├── in/
    │   │   │               │   │   └── web/
    │   │   │               │   │       ├── HealthcheckController.kt
    │   │   │               │   │       ├── ResumeAdminController.kt
    │   │   │               │   │       └── StreamChatWebSocketHandler.kt
    │   │   │               │   └── out/
    │   │   │               │       ├── gemini/
    │   │   │               │       │   ├── GeminiAdapter.kt
    │   │   │               │       │   └── GeminiApiEmbeddingAdapter.kt
    │   │   │               │       └── persistence/
    │   │   │               │           ├── ChatHistoryDocument.kt
    │   │   │               │           ├── ChatHistoryDocumentRepository.kt
    │   │   │               │           ├── ChatHistoryRepositoryAdapter.kt
    │   │   │               │           ├── MongoVectorAdapter.kt
    │   │   │               │           ├── ResumeChunk.kt
    │   │   │               │           ├── ResumeChunkDocument.kt
    │   │   │               │           ├── ResumeFileAdapter.kt
    │   │   │               │           ├── ResumePersistenceAdapter.kt
    │   │   │               │           └── VectorDBPort.kt
    │   │   │               ├── application/
    │   │   │               │   ├── port/
    │   │   │               │   │   ├── in/
    │   │   │               │   │   │   ├── ChatUseCase.kt
    │   │   │               │   │   │   └── ManageResumeUseCase.kt
    │   │   │               │   │   └── out/
    │   │   │               │   │       ├── ChatHistoryRepository.kt
    │   │   │               │   │       ├── EmbeddingPort.kt
    │   │   │               │   │       ├── GeminiPort.kt
    │   │   │               │   │       ├── LoadResumePort.kt
    │   │   │               │   │       ├── ResumePersistencePort.kt
    │   │   │               │   │       └── ResumeProviderPort.kt
    │   │   │               │   └── service/
    │   │   │               │       ├── dto/
    │   │   │               │       │   ├── QueryType.kt
    │   │   │               │       │   └── RouteDecision.kt
    │   │   │               │       ├── ChatService.kt
    │   │   │               │       ├── ContextRetriever.kt
    │   │   │               │       ├── LLMRouter.kt
    │   │   │               │       ├── ManageResumeService.kt
    │   │   │               │       ├── ResumeChunkingService.kt
    │   │   │               │       └── ResumeDataProvider.kt
    │   │   │               ├── common/
    │   │   │               │   ├── config/
    │   │   │               │   │   ├── CorsConfig.kt
    │   │   │               │   │   ├── GeminiConfig.kt
    │   │   │               │   │   ├── PromptProperties.kt
    │   │   │               │   │   └── WebSocketConfig.kt
    │   │   │               │   └── util/
    │   │   │               │       └── ChunkIdGenerator.kt
    │   │   │               ├── domain/
    │   │   │               │   ├── ChatHistory.kt
    │   │   │               │   ├── ChatMessage.kt
    │   │   │               │   ├── MessageType.kt
    │   │   │               │   ├── ResumeSection.kt
    │   │   │               │   └── StreamMessage.kt
    │   │   │               └── WhoAmAiApplication.kt
    │   │   └── resources/
    │   │       ├── application.yml
    │   │       ├── atlas-index.json
    │   │       └── resume.json
    │   └── test/
    │       └── kotlin/
    │           └── com/
    │               └── dd3ok/
    │                   └── whoamai/
    │                       └── WhoAmAiApplicationTests.kt
    ├── .gitattributes
    ├── .gitignore
    ├── build.gradle.kts
    ├── Dockerfile
    ├── gradlew
    ├── gradlew.bat
    ├── readme.md
    └── settings.gradle.kts
```

## 📜 선택된 파일 코드

### `src/main/kotlin/com/dd3ok/whoamai/WhoAmAiApplication.kt`
```kotlin
package com.dd3ok.whoamai

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class WhoAmAiApplication

fun main(args: Array<String>) {
    runApplication<WhoAmAiApplication>(*args)
}

```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/in/web/HealthcheckController.kt`
```kotlin
package com.dd3ok.whoamai.adapter.`in`.web

import com.dd3ok.whoamai.adapter.out.persistence.ChatHistoryDocumentRepository
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/healthcheck")
class HealthcheckController(
    private val chatHistoryRepository: ChatHistoryDocumentRepository
) {

    @GetMapping
    suspend fun healthcheck(): ResponseEntity<Long> {
        val count = chatHistoryRepository.count()
        return ResponseEntity.ok(count)
    }
}

```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/in/web/ResumeAdminController.kt`
```kotlin
package com.dd3ok.whoamai.adapter.`in`.web

import com.dd3ok.whoamai.application.port.`in`.ManageResumeUseCase
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/admin")
class ResumeAdminController(
    private val manageResumeUseCase: ManageResumeUseCase
) {

    @PostMapping("/resume/reindex")
    suspend fun reindex(): ResponseEntity<String> {
        val resultMessage = manageResumeUseCase.reindexResumeData()
        return if (resultMessage.contains("finished")) {
            ResponseEntity.ok(resultMessage)
        } else {
            ResponseEntity.internalServerError().body(resultMessage)
        }
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/in/web/StreamChatWebSocketHandler.kt`
```kotlin
package com.dd3ok.whoamai.adapter.`in`.web

import com.dd3ok.whoamai.application.port.`in`.ChatUseCase
import com.dd3ok.whoamai.domain.StreamMessage
import com.fasterxml.jackson.databind.ObjectMapper
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.reactive.asFlow
import kotlinx.coroutines.reactive.awaitFirstOrNull
import kotlinx.coroutines.reactor.asFlux
import kotlinx.coroutines.reactor.mono
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component
import org.springframework.web.reactive.socket.WebSocketHandler
import org.springframework.web.reactive.socket.WebSocketSession
import reactor.core.publisher.Mono

@Component
class StreamChatWebSocketHandler(
    private val chatUseCase: ChatUseCase,
    private val objectMapper: ObjectMapper
) : WebSocketHandler {

    private val logger = LoggerFactory.getLogger(javaClass)

    override fun handle(session: WebSocketSession): Mono<Void> = mono {
        handleChatSession(session)
    }.then()

    private suspend fun handleChatSession(session: WebSocketSession) {
        session.receive()
            .map { it.payloadAsText }
            .asFlow()
            .collect { json ->
                try {
                    val userMessage = objectMapper.readValue(json, StreamMessage::class.java)

                    val responseFlow = chatUseCase.streamChatResponse(userMessage)
                        .map { aiToken -> session.textMessage(aiToken) }
                        .asFlux()

                    session.send(responseFlow).awaitFirstOrNull()
                } catch (e: Exception) {
                    logger.error("Failed to process message from session ${session.id}: ${e.message}", e)
                    // session.send(Mono.just(session.textMessage("Invalid message format."))).awaitFirstOrNull()
                }
            }
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/out/gemini/GeminiAdapter.kt`
```kotlin
package com.dd3ok.whoamai.adapter.out.gemini

import com.dd3ok.whoamai.application.port.out.GeminiPort
import com.dd3ok.whoamai.common.config.GeminiModelProperties
import com.dd3ok.whoamai.domain.ChatMessage
import com.google.genai.Client
import com.google.genai.types.Content
import com.google.genai.types.GenerateContentConfig
import com.google.genai.types.Part
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOf
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Qualifier
import org.springframework.stereotype.Component

@Component
class GeminiAdapter(
    private val client: Client,
    private val modelProperties: GeminiModelProperties,
    @Qualifier("generationConfig") private val generationConfig: GenerateContentConfig,
    @Qualifier("routingConfig") private val routingConfig: GenerateContentConfig,
    @Qualifier("summarizationConfig") private val summarizationConfig: GenerateContentConfig
) : GeminiPort {

    private val logger = LoggerFactory.getLogger(javaClass)

    override suspend fun generateChatContent(history: List<ChatMessage>): Flow<String> {
        val apiHistory = history.map { msg ->
            Content.builder()
                .role(msg.role)
                .parts(Part.fromText(msg.text))
                .build()
        }

        return try {
            val responseStream = client.models
                .generateContentStream(modelProperties.name, apiHistory, generationConfig)

            flow {
                for (response in responseStream) {
                    response.text()?.let { emit(it) }
                }
            }
        } catch (e: Exception) {
            logger.error("Error while calling Gemini API: ${e.message}", e)
            flowOf("죄송합니다, AI 응답 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
        }
    }

    override suspend fun generateContent(prompt: String, purpose: String): String {
        val config = when (purpose) {
            "routing" -> routingConfig
            "summarization" -> summarizationConfig
            else -> generationConfig
        }

        return try {
            val response = client.models.generateContent(modelProperties.name, prompt, config)
            response.text() ?: ""
        } catch (e: Exception) {
            logger.error("Error while calling Gemini API for purpose '$purpose': ${e.message}", e)
            ""
        }
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/out/gemini/GeminiApiEmbeddingAdapter.kt`
```kotlin
package com.dd3ok.whoamai.adapter.out.gemini

import com.dd3ok.whoamai.application.port.out.EmbeddingPort
import com.google.genai.Client
import com.google.genai.types.EmbedContentConfig
import com.google.genai.types.EmbedContentResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component

@Component
class GeminiApiEmbeddingAdapter(
    @Value("\${gemini.api.key}") private val apiKey: String,
    @Value("\${gemini.model.text}") private val modelName: String
) : EmbeddingPort {

    private val logger = LoggerFactory.getLogger(javaClass)

    private val client: Client by lazy {
        logger.info("Initializing Google Gen AI Client for Embedding...")
        Client.builder()
            .apiKey(apiKey)
            .build()
    }

    override suspend fun embedContent(text: String): List<Float> = withContext(Dispatchers.IO) {
        try {
            val config = EmbedContentConfig.builder().build()
            val response: EmbedContentResponse = client.models.embedContent(modelName, text, config)

            val embeddingList = response.embeddings().orElse(emptyList())

            if (embeddingList.isNotEmpty()) {
                val firstEmbedding = embeddingList.first()
                return@withContext firstEmbedding.values().orElse(emptyList())
            } else {
                logger.error("Embedding list was empty for the response.")
                return@withContext emptyList()
            }

        } catch (e: Exception) {
            logger.error("Error while calling Gemini API for embedding: ${e.message}", e)
            emptyList<Float>()
        }
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/out/persistence/ChatHistoryDocument.kt`
```kotlin
package com.dd3ok.whoamai.adapter.out.persistence

import com.dd3ok.whoamai.domain.ChatMessage
import org.springframework.data.annotation.Id
import org.springframework.data.mongodb.core.mapping.Document

@Document(collection = "chat_histories")
data class ChatHistoryDocument(
    @Id
    val userId: String,
    val messages: MutableList<ChatMessage> = mutableListOf()
)
```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/out/persistence/ChatHistoryDocumentRepository.kt`
```kotlin
package com.dd3ok.whoamai.adapter.out.persistence

import org.springframework.data.repository.kotlin.CoroutineCrudRepository

interface ChatHistoryDocumentRepository : CoroutineCrudRepository<ChatHistoryDocument, String>
```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/out/persistence/ChatHistoryRepositoryAdapter.kt`
```kotlin
package com.dd3ok.whoamai.adapter.out.persistence

import com.dd3ok.whoamai.application.port.out.ChatHistoryRepository
import com.dd3ok.whoamai.domain.ChatHistory
import org.springframework.stereotype.Repository

@Repository
class ChatHistoryRepositoryAdapter(
    private val documentRepository: ChatHistoryDocumentRepository
) : ChatHistoryRepository {

    private fun ChatHistoryDocument.toDomain() = ChatHistory(this.userId, this.messages)

    private fun ChatHistory.toEntity() = ChatHistoryDocument(this.userId, this.history.toMutableList())

    override suspend fun findByUserId(userId: String): ChatHistory? {
        return documentRepository.findById(userId)?.toDomain()
    }

    override suspend fun save(chatHistory: ChatHistory): ChatHistory {
        val entity = chatHistory.toEntity()
        return documentRepository.save(entity).toDomain()
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/out/persistence/MongoVectorAdapter.kt`
```kotlin
package com.dd3ok.whoamai.adapter.out.persistence

import com.dd3ok.whoamai.application.port.out.EmbeddingPort
import kotlinx.coroutines.reactor.awaitSingle
import kotlinx.coroutines.reactor.awaitSingleOrNull
import kotlinx.coroutines.reactor.mono
import org.bson.Document
import org.slf4j.LoggerFactory
import org.springframework.data.mongodb.core.ReactiveMongoTemplate
import org.springframework.data.mongodb.core.aggregation.Aggregation
import org.springframework.data.mongodb.core.aggregation.TypedAggregation
import org.springframework.data.mongodb.core.findById
import org.springframework.stereotype.Component
import reactor.core.publisher.Flux
import reactor.core.publisher.Mono

@Component
class MongoVectorAdapter(
    private val mongoTemplate: ReactiveMongoTemplate,
    private val embeddingPort: EmbeddingPort
) : VectorDBPort {

    private val logger = LoggerFactory.getLogger(javaClass)

    companion object {
        const val COLLECTION_NAME = "resume_chunks"
        // Vector Search 전용 인덱스를 사용하도록 이름을 변경하거나,
        // 기존 Atlas Search 인덱스를 삭제하고 Vector Search 타입으로 다시 생성해야 합니다.
        const val VECTOR_INDEX_NAME = "vector_index"
        private const val NUM_CANDIDATES_MULTIPLIER = 10
    }

    override suspend fun indexResume(chunks: List<ResumeChunk>): Int {
        // 이 부분은 변경 사항 없습니다.
        return mongoTemplate.dropCollection(ResumeChunkDocument::class.java)
            .thenMany(
                Flux.fromIterable(chunks)
                    .flatMap { chunk ->
                        mono { embeddingPort.embedContent(chunk.content) }
                            .map { embedding ->
                                ResumeChunkDocument(
                                    id = chunk.id,
                                    type = chunk.type,
                                    content = chunk.content,
                                    contentEmbedding = embedding,
                                    company = chunk.company,
                                    skills = chunk.skills,
                                    source = chunk.source
                                )
                            }
                            .doOnError { error -> logger.error("Failed to create embedding for chunk: ${chunk.id}. Skipping.", error) }
                            .onErrorResume { Mono.empty() }
                    }
            )
            .collectList()
            .flatMap { documents ->
                if (documents.isNotEmpty()) {
                    mongoTemplate.insertAll(documents).then(Mono.just(documents.size))
                } else {
                    Mono.just(0)
                }
            }
            .doOnSuccess { indexedCount ->
                logger.info("Successfully indexed $indexedCount resume chunks into MongoDB Atlas.")
            }
            .awaitSingle()
    }

    // 가장 안정적인 $vectorSearch 방식으로 회귀
    override suspend fun searchSimilarResumeSections(query: String, topK: Int, filter: Document?): List<String> {
        val queryEmbedding = embeddingPort.embedContent(query)
        if (queryEmbedding.isEmpty()) {
            logger.warn("Query embedding failed. Returning empty search results.")
            return emptyList()
        }
        val vectorSearchStage = Aggregation.stage(
            Document("\$vectorSearch",
                Document("index", VECTOR_INDEX_NAME)
                    .append("path", "content_embedding")
                    .append("queryVector", queryEmbedding)
                    .append("numCandidates", (topK * NUM_CANDIDATES_MULTIPLIER).toLong())
                    .append("limit", topK.toLong())
                    .apply {
                        filter?.let { append("filter", it) }
                    }
            )
        )
        val projectStage = Aggregation.project("content").andExclude("_id")

        val aggregation: TypedAggregation<ResumeChunkDocument> = Aggregation.newAggregation(
            ResumeChunkDocument::class.java,
            vectorSearchStage,
            projectStage
        )

        return mongoTemplate.aggregate(aggregation, COLLECTION_NAME, Document::class.java)
            .mapNotNull { it.getString("content") }
            .collectList()
            .awaitSingleOrNull() ?: emptyList()
    }

    override suspend fun findChunkById(id: String): String? {
        return mongoTemplate.findById<ResumeChunkDocument>(id)
            .map { it.content }
            .awaitSingleOrNull()
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/out/persistence/ResumeChunk.kt`
```kotlin
package com.dd3ok.whoamai.adapter.out.persistence

data class ResumeChunk(
    val id: String,
    val type: String,
    val content: String,
    val company: String? = null,
    val skills: List<String>? = null,
    val source: Map<String, Any>
)
```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/out/persistence/ResumeChunkDocument.kt`
```kotlin
package com.dd3ok.whoamai.adapter.out.persistence

import org.springframework.data.annotation.Id
import org.springframework.data.mongodb.core.mapping.Document
import org.springframework.data.mongodb.core.mapping.Field

@Document(collection = MongoVectorAdapter.COLLECTION_NAME)
data class ResumeChunkDocument(
    @Id
    val id: String,

    @Field("chunk_type")
    val type: String,

    @Field("content_text")
    val content: String,

    @Field("content_embedding")
    val contentEmbedding: List<Float>,

    @Field("company")
    val company: String? = null,

    @Field("skills")
    val skills: List<String>? = emptyList(),

    @Field("source_data")
    val source: Map<String, Any>
)
```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/out/persistence/ResumeFileAdapter.kt`
```kotlin
package com.dd3ok.whoamai.adapter.out.persistence

import com.dd3ok.whoamai.application.port.out.LoadResumePort
import com.dd3ok.whoamai.domain.Resume
import com.fasterxml.jackson.databind.ObjectMapper
import org.slf4j.LoggerFactory
import org.springframework.core.io.ClassPathResource
import org.springframework.stereotype.Component

@Component
class ResumeFileAdapter(private val objectMapper: ObjectMapper) : LoadResumePort {

    private val logger = LoggerFactory.getLogger(javaClass)

    override fun load(): Resume {
        return try {
            logger.info("Loading resume data from 'resume.json' file.")
            val resource = ClassPathResource("resume.json")
            objectMapper.readValue(resource.inputStream, Resume::class.java)
        } catch (e: Exception) {
            logger.error("FATAL: Failed to load and parse resume.json. Returning an empty Resume object.", e)
            Resume()
        }
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/out/persistence/ResumePersistenceAdapter.kt`
```kotlin
package com.dd3ok.whoamai.adapter.out.persistence

import com.dd3ok.whoamai.application.port.out.ResumePersistencePort
import com.dd3ok.whoamai.application.service.ResumeChunkingService
import com.dd3ok.whoamai.domain.Resume
import org.bson.Document
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component

@Component
class ResumePersistenceAdapter(
    private val vectorDBPort: VectorDBPort,
    private val resumeChunkingService: ResumeChunkingService
) : ResumePersistencePort {

    private val logger = LoggerFactory.getLogger(javaClass)

    override suspend fun index(resume: Resume): Int {
        logger.info("Delegating resume chunking to ResumeChunkingService.")
        val chunks = resumeChunkingService.generateChunks(resume)

        if (chunks.isEmpty()) {
            logger.warn("No resume chunks were generated. Indexing skipped.")
            return 0
        }

        return vectorDBPort.indexResume(chunks)
    }

    override suspend fun findContentById(id: String): String? {
        return vectorDBPort.findChunkById(id)
    }

    override suspend fun searchSimilarSections(query: String, topK: Int, filter: Document?): List<String> {
        return vectorDBPort.searchSimilarResumeSections(query, topK, filter)
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/adapter/out/persistence/VectorDBPort.kt`
```kotlin
package com.dd3ok.whoamai.adapter.out.persistence

import org.bson.Document

interface VectorDBPort {
    suspend fun indexResume(chunks: List<ResumeChunk>): Int
    suspend fun searchSimilarResumeSections(query: String, topK: Int, filter: Document? = null): List<String>
    suspend fun findChunkById(id: String): String?
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/port/in/ChatUseCase.kt`
```kotlin
package com.dd3ok.whoamai.application.port.`in`

import com.dd3ok.whoamai.domain.StreamMessage
import kotlinx.coroutines.flow.Flow

interface ChatUseCase {
    suspend fun streamChatResponse(message: StreamMessage): Flow<String>
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/port/in/ManageResumeUseCase.kt`
```kotlin
package com.dd3ok.whoamai.application.port.`in`

interface ManageResumeUseCase {
    suspend fun reindexResumeData(): String
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/port/out/ChatHistoryRepository.kt`
```kotlin
package com.dd3ok.whoamai.application.port.out

import com.dd3ok.whoamai.domain.ChatHistory

interface ChatHistoryRepository {
    suspend fun findByUserId(userId: String): ChatHistory?
    suspend fun save(chatHistory: ChatHistory): ChatHistory
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/port/out/EmbeddingPort.kt`
```kotlin
package com.dd3ok.whoamai.application.port.out

interface EmbeddingPort {
    suspend fun embedContent(text: String): List<Float>
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/port/out/GeminiPort.kt`
```kotlin
package com.dd3ok.whoamai.application.port.out

import com.dd3ok.whoamai.domain.ChatMessage
import kotlinx.coroutines.flow.Flow

interface GeminiPort {
    suspend fun generateChatContent(history: List<ChatMessage>): Flow<String>
    suspend fun generateContent(prompt: String, purpose: String): String
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/port/out/LoadResumePort.kt`
```kotlin
package com.dd3ok.whoamai.application.port.out

import com.dd3ok.whoamai.domain.Resume

interface LoadResumePort {
    fun load(): Resume
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/port/out/ResumePersistencePort.kt`
```kotlin
package com.dd3ok.whoamai.application.port.out

import com.dd3ok.whoamai.domain.Resume
import org.bson.Document

interface ResumePersistencePort {
    suspend fun index(resume: Resume): Int

    suspend fun findContentById(id: String): String?

    suspend fun searchSimilarSections(query: String, topK: Int, filter: Document? = null): List<String>
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/port/out/ResumeProviderPort.kt`
```kotlin
package com.dd3ok.whoamai.application.port.out

import com.dd3ok.whoamai.domain.Resume

interface ResumeProviderPort {
    fun getResume(): Resume
    fun isInitialized(): Boolean
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/service/ChatService.kt`
```kotlin
package com.dd3ok.whoamai.application.service

import com.dd3ok.whoamai.application.port.`in`.ChatUseCase
import com.dd3ok.whoamai.application.port.out.ChatHistoryRepository
import com.dd3ok.whoamai.application.port.out.GeminiPort
import com.dd3ok.whoamai.application.service.dto.QueryType
import com.dd3ok.whoamai.common.config.PromptProperties
import com.dd3ok.whoamai.domain.ChatHistory
import com.dd3ok.whoamai.domain.ChatMessage
import com.dd3ok.whoamai.domain.StreamMessage
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.onCompletion
import kotlinx.coroutines.flow.onEach
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service

@Service
class ChatService(
    private val geminiPort: GeminiPort,
    private val chatHistoryRepository: ChatHistoryRepository,
    private val llmRouter: LLMRouter,
    private val contextRetriever: ContextRetriever,
    private val promptProperties: PromptProperties
) : ChatUseCase {

    private val logger = LoggerFactory.getLogger(javaClass)

    private companion object {
        const val API_WINDOW_TOKENS = 2048
        const val SUMMARY_TRIGGER_TOKENS = 4096
        const val SUMMARY_SOURCE_MESSAGES = 5
    }

    override suspend fun streamChatResponse(message: StreamMessage): Flow<String> {
        val userId = message.uuid
        val userPrompt = message.content

        val domainHistory = chatHistoryRepository.findByUserId(userId) ?: ChatHistory(userId = userId)
        val pastHistory = createApiHistoryWindow(domainHistory)

        // 1. ContextRetriever를 먼저 호출하여 규칙 기반 검색을 시도
        var relevantContexts = contextRetriever.retrieveByRule(userPrompt)

        // 2. 규칙 기반으로 컨텍스트를 찾지 못했다면, 그 때 LLM 라우터와 벡터 검색을 사용
        if (relevantContexts.isEmpty()) {
            val routeDecision = llmRouter.route(userPrompt)
            logger.info("No rule match. LLM Router hint: $routeDecision")
            if (routeDecision.queryType == QueryType.RESUME_RAG) {
                relevantContexts = contextRetriever.retrieveByVector(userPrompt, routeDecision)
            }
        }

        // 3. 최종적으로 컨텍스트 존재 여부에 따라 프롬프트 결정
        val finalHistory = if (relevantContexts.isNotEmpty()) {
            logger.info("Context found. Proceeding with RAG prompt.")
            createRagPrompt(pastHistory, userPrompt, relevantContexts)
        } else {
            logger.info("No context found. Proceeding with conversational prompt.")
            createConversationalPrompt(pastHistory, userPrompt)
        }

        // 4. LLM 호출 및 결과 스트리밍
        val modelResponseBuilder = StringBuilder()
        return geminiPort.generateChatContent(finalHistory)
            .onEach { chunk -> modelResponseBuilder.append(chunk) }
            .onCompletion { cause ->
                if (cause == null) {
                    val fullResponse = modelResponseBuilder.toString()
                    // 5. 대화 기록 저장
                    saveHistory(userId, userPrompt, fullResponse)
                } else {
                    logger.error("Chat stream failed with cause. History NOT saved.", cause)
                }
            }
    }

    private suspend fun saveHistory(userId: String, userPrompt: String, modelResponse: String) {
        val currentHistory = chatHistoryRepository.findByUserId(userId) ?: ChatHistory(userId = userId)
        currentHistory.addMessage(ChatMessage(role = "user", text = userPrompt))
        currentHistory.addMessage(ChatMessage(role = "model", text = modelResponse))
        val finalHistoryToSave = summarizeHistoryIfNeeded(currentHistory)
        chatHistoryRepository.save(finalHistoryToSave)
        logger.info("[SUCCESS] History for user {} saved.", userId)
    }

    private fun createRagPrompt(history: List<ChatMessage>, userPrompt: String, contexts: List<String>): List<ChatMessage> {
        val contextString = if (contexts.isNotEmpty()) contexts.joinToString("\n---\n") else "관련 정보 없음"
        val finalUserPrompt = promptProperties.ragTemplate
            .replace("{context}", contextString)
            .replace("{question}", userPrompt)

        return history + ChatMessage(role = "user", text = finalUserPrompt)
    }

    private fun createConversationalPrompt(history: List<ChatMessage>, userPrompt: String): List<ChatMessage> {
        val finalUserPrompt = promptProperties.conversationalTemplate
            .replace("{question}", userPrompt)

        return history + ChatMessage(role = "user", text = finalUserPrompt)
    }

    private fun createApiHistoryWindow(domainHistory: ChatHistory): List<ChatMessage> {
        var currentTokens = 0
        val recentMessages = mutableListOf<ChatMessage>()
        for (msg in domainHistory.history.reversed()) {
            val estimatedTokens = estimateTokens(msg.text)
            if (currentTokens + estimatedTokens > API_WINDOW_TOKENS) {
                break
            }
            recentMessages.add(msg)
            currentTokens += estimatedTokens
        }
        recentMessages.reverse()
        return recentMessages
    }

    private suspend fun summarizeHistoryIfNeeded(originalHistory: ChatHistory): ChatHistory {
        val totalTokens = originalHistory.history.sumOf { estimateTokens(it.text) }
        if (totalTokens < SUMMARY_TRIGGER_TOKENS || originalHistory.history.size < SUMMARY_SOURCE_MESSAGES + 2) {
            return originalHistory
        }

        logger.info("History for user {} exceeds token threshold. Starting summarization.", originalHistory.userId)
        val messagesToSummarize = originalHistory.history.take(SUMMARY_SOURCE_MESSAGES)
        val recentMessages = originalHistory.history.drop(SUMMARY_SOURCE_MESSAGES)
        val summarizationPrompt = """다음 대화의 핵심 내용을 한두 문단으로 간결하게 요약해주세요. --- ${messagesToSummarize.joinToString("\n") { "[${it.role}]: ${it.text}" }} --- 요약:""".trimIndent()
        val summaryText = geminiPort.generateContent(summarizationPrompt, "summarization")

        if (summaryText.isBlank()) {
            logger.warn("Summarization failed or returned empty. Skipping history modification.")
            return originalHistory
        }
        val summaryMessage = ChatMessage(role = "model", text = "이전 대화 요약: $summaryText")
        val newMessages = mutableListOf(summaryMessage).apply { addAll(recentMessages) }
        return ChatHistory(originalHistory.userId, newMessages)
    }

    private fun estimateTokens(text: String): Int = (text.length * 1.5).toInt()
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/service/ContextRetriever.kt`
```kotlin
package com.dd3ok.whoamai.application.service

import com.dd3ok.whoamai.application.port.out.ResumePersistencePort
import com.dd3ok.whoamai.application.port.out.ResumeProviderPort
import com.dd3ok.whoamai.application.service.dto.RouteDecision
import com.dd3ok.whoamai.common.util.ChunkIdGenerator
import org.bson.Document
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component

@Component
class ContextRetriever(
    private val resumePersistencePort: ResumePersistencePort,
    private val resumeProviderPort: ResumeProviderPort
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    private val rules: List<(String, String) -> String?> by lazy {
        listOf(
            { query, name -> if (listOf("누구야", "누구세요", "소개", "자기소개", name).any { query.contains(it) }) ChunkIdGenerator.forSummary() else null },
            { query, _ -> if (listOf("총 경력", "총경력", "전체경력").any { query.contains(it) }) ChunkIdGenerator.forTotalExperience() else null },
            { query, _ -> if (listOf("프로젝트", "project").any { query.contains(it) }) "projects" else null },
            { query, _ -> if (listOf("경력", "이력", "회사").any { query.contains(it) }) "experiences" else null },
            { query, _ -> if (listOf("자격증", "certificate").any { query.contains(it) }) ChunkIdGenerator.forCertificates() else null },
            { query, _ -> if (listOf("관심사", "interest").any { query.contains(it) }) ChunkIdGenerator.forInterests() else null },
            { query, _ -> if (listOf("기술", "스킬", "스택").any { query.contains(it) }) ChunkIdGenerator.forSkills() else null },
            { query, _ -> if (listOf("학력", "학교", "대학").any { query.contains(it) }) ChunkIdGenerator.forEducation() else null },
            { query, _ -> if (listOf("mbti", "성격").any { query.contains(it) }) ChunkIdGenerator.forMbti() else null },
            { query, _ -> if (listOf("취미", "여가시간").any { query.contains(it) }) ChunkIdGenerator.forHobbies() else null }
        )
    }

    /**
     * 규칙 기반으로 컨텍스트를 검색합니다.
     * @return 컨텍스트를 찾으면 List<String>, 못 찾으면 빈 List를 반환합니다.
     */
    suspend fun retrieveByRule(userPrompt: String): List<String> {
        val resume = resumeProviderPort.getResume()
        val normalizedQuery = userPrompt.replace(Regex("\\s+"), "").lowercase()
        val resumeName = resume.name.lowercase()

        // 1. Specific project title check
        val matchedProject = resume.projects.find { userPrompt.contains(it.title) }
        if (matchedProject != null) {
            logger.info("Context retrieved by: Specific Project Rule ('${matchedProject.title}').")
            val projectId = ChunkIdGenerator.forProject(matchedProject.title)
            return resumePersistencePort.findContentById(projectId)?.let { listOf(it) } ?: emptyList()
        }

        // 2. General rule-based check
        for (rule in rules) {
            val result = rule(normalizedQuery, resumeName)
            if (result != null) {
                logger.info("Context retrieved by: General Rule ('$result').")
                return when (result) {
                    "projects" -> resume.projects.mapNotNull {
                        resumePersistencePort.findContentById(ChunkIdGenerator.forProject(it.title))
                    }
                    "experiences" -> resume.experiences.mapNotNull {
                        resumePersistencePort.findContentById(ChunkIdGenerator.forExperience(it.company))
                    }
                    else -> resumePersistencePort.findContentById(result)?.let { listOf(it) } ?: emptyList()
                }
            }
        }

        return emptyList() // 규칙에 맞는 것이 없으면 빈 리스트 반환
    }

    /**
     * LLM 라우터의 힌트를 바탕으로 벡터 검색을 수행합니다.
     */
    suspend fun retrieveByVector(userPrompt: String, routeDecision: RouteDecision): List<String> {
        logger.info("No rules matched. Context retrieved by: Vector Search (as per LLMRouter).")
        val filters = mutableListOf<Document>()
        routeDecision.company?.let {
            filters.add(Document("company", Document("\$eq", it)))
        }
        routeDecision.skills?.takeIf { it.isNotEmpty() }?.let {
            filters.add(Document("skills", Document("\$in", it)))
        }

        val finalFilter = if (filters.isNotEmpty()) {
            Document("\$and", filters)
        } else {
            null
        }

        val searchKeywords = routeDecision.keywords?.joinToString(" ") ?: ""
        val finalQuery = "$userPrompt $searchKeywords".trim()

        return resumePersistencePort.searchSimilarSections(finalQuery, topK = 3, filter = finalFilter)
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/service/LLMRouter.kt`
```kotlin
package com.dd3ok.whoamai.application.service

import com.dd3ok.whoamai.application.port.out.GeminiPort
import com.dd3ok.whoamai.application.port.out.ResumeProviderPort
import com.dd3ok.whoamai.application.service.dto.QueryType
import com.dd3ok.whoamai.application.service.dto.RouteDecision
import com.dd3ok.whoamai.common.config.PromptProperties
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component

@Component
class LLMRouter(
    private val geminiPort: GeminiPort,
    private val resumeProviderPort: ResumeProviderPort,
    private val promptProperties: PromptProperties, // PromptProperties 주입
    private val objectMapper: ObjectMapper
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    suspend fun route(userPrompt: String): RouteDecision {
        val resume = resumeProviderPort.getResume()
        val companies = resume.experiences.map { it.company }
        val skills = resume.skills

        val prompt = promptProperties.routingTemplate
            .replace("{resume_owner_name}", resume.name)
            .replace("{companies_list}", companies.joinToString(", "))
            .replace("{skills_list}", skills.joinToString(", "))
            .replace("{question}", userPrompt)

        try {
            val responseJson = geminiPort.generateContent(prompt, "routing")
            if (responseJson.isBlank()) {
                logger.warn("LLM Router returned a blank response. Defaulting to NON_RAG.")
                return RouteDecision(QueryType.NON_RAG)
            }
            val pureJson = responseJson.substringAfter("```json").substringBeforeLast("```").trim()
            return objectMapper.readValue(pureJson)
        } catch (e: Exception) {
            logger.error("Error parsing LLM Router response. Defaulting to NON_RAG. Error: ${e.message}", e)
            return RouteDecision(QueryType.NON_RAG)
        }
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/service/ManageResumeService.kt`
```kotlin
package com.dd3ok.whoamai.application.service

import com.dd3ok.whoamai.application.port.`in`.ManageResumeUseCase
import com.dd3ok.whoamai.application.port.out.ResumePersistencePort // <-- 올바른 포트를 import 합니다.
import com.dd3ok.whoamai.application.port.out.ResumeProviderPort

import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service

@Service
class ManageResumeService(
    private val resumeProviderPort: ResumeProviderPort,
    private val resumePersistencePort: ResumePersistencePort
) : ManageResumeUseCase {

    private val logger = LoggerFactory.getLogger(javaClass)

    override suspend fun reindexResumeData(): String {
        if (!resumeProviderPort.isInitialized()) {
            val errorMessage = "Resume data is not loaded. Cannot perform re-indexing."
            logger.error(errorMessage)
            return errorMessage
        }

        val indexedCount = resumePersistencePort.index(resumeProviderPort.getResume())

        val successMessage = "Resume indexing process finished. Indexed $indexedCount documents."
        logger.info(successMessage)
        return successMessage
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/service/ResumeChunkingService.kt`
```kotlin
package com.dd3ok.whoamai.application.service

import com.dd3ok.whoamai.adapter.out.persistence.ResumeChunk
import com.dd3ok.whoamai.common.util.ChunkIdGenerator
import com.dd3ok.whoamai.domain.*
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.convertValue
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service

/**
 * Domain 객체(Resume)를 Persistence Layer에서 사용할 DTO(ResumeChunk)로
 * 변환(Chunking)하는 비즈니스 로직을 담당합니다.
 */
@Service
class ResumeChunkingService(
    private val objectMapper: ObjectMapper
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    fun generateChunks(resume: Resume): List<ResumeChunk> {
        return try {
            val chunks = mutableListOf<ResumeChunk>()

            chunks.add(createSummaryChunk(resume))
            chunks.add(createSkillsChunk(resume))
            chunks.add(createTotalExperienceChunk(resume))
            createEducationChunk(resume)?.let { chunks.add(it) }
            createCertificatesChunk(resume)?.let { chunks.add(it) }
            createHobbiesChunk(resume)?.let { chunks.add(it) }
            createInterestsChunk(resume)?.let { chunks.add(it) }
            createMbtiChunk(resume)?.let { chunks.add(it) }
            chunks.addAll(createExperienceChunks(resume))
            chunks.addAll(createProjectChunks(resume))

            logger.info("Translated domain object into ${chunks.size} infrastructure DTOs.")
            chunks
        } catch (e: Exception) {
            logger.error("Error during chunk generation: ${e.message}", e)
            emptyList()
        }
    }

    private fun createSummaryChunk(resume: Resume): ResumeChunk {
        val summaryContent = "저는 ${resume.name}입니다. ${resume.summary}"
        return ResumeChunk(
            id = ChunkIdGenerator.forSummary(),
            type = "summary",
            content = summaryContent,
            source = objectMapper.convertValue(
                mapOf(
                    "name" to resume.name,
                    "summary" to resume.summary,
                    "blog" to resume.blog
                )
            )
        )
    }

    private fun createSkillsChunk(resume: Resume): ResumeChunk {
        val content = "보유하고 있는 주요 기술은 ${resume.skills.joinToString(", ")} 등 입니다."
        return ResumeChunk(
            id = ChunkIdGenerator.forSkills(),
            type = "skills",
            content = content,
            skills = resume.skills,
            source = objectMapper.convertValue(mapOf("skills" to resume.skills))
        )
    }

    private fun createTotalExperienceChunk(resume: Resume): ResumeChunk {
        val content = "전체 경력 기간 정보는 다음과 같습니다: " +
                resume.experiences.joinToString("; ") { exp ->
                    "${exp.company}에서 ${exp.period.start}부터 ${exp.period.end}까지 근무"
                } + ". 이 정보를 바탕으로 총 경력을 계산해서 알려주세요."
        return ResumeChunk(
            id = ChunkIdGenerator.forTotalExperience(),
            type = "summary",
            content = content,
            source = objectMapper.convertValue(mapOf("items" to resume.experiences))
        )
    }

    private fun createEducationChunk(resume: Resume): ResumeChunk? {
        if (resume.education.isEmpty()) return null
        val content = "학력 정보는 다음과 같습니다.\n" + resume.education.joinToString("\n") { edu ->
            "${edu.school}에서 ${edu.major}을 전공했으며(${edu.period.start} ~ ${edu.period.end}), ${edu.degree} 학위를 받았습니다."
        }
        return ResumeChunk(
            id = ChunkIdGenerator.forEducation(),
            type = "education",
            content = content,
            source = objectMapper.convertValue(mapOf("items" to resume.education))
        )
    }

    private fun createCertificatesChunk(resume: Resume): ResumeChunk? {
        if (resume.certificates.isEmpty()) return null
        val content = "보유 자격증은 다음과 같습니다.\n" + resume.certificates.joinToString("\n") { cert ->
            "${cert.issuedAt}에 ${cert.issuer}에서 발급한 ${cert.title} 자격증을 보유하고 있습니다."
        }
        return ResumeChunk(
            id = ChunkIdGenerator.forCertificates(),
            type = "certificate",
            content = content,
            source = objectMapper.convertValue(mapOf("items" to resume.certificates))
        )
    }

    private fun createHobbiesChunk(resume: Resume): ResumeChunk? {
        if (resume.hobbies.isEmpty()) return null
        val content = "주요 취미는 다음과 같습니다.\n" + resume.hobbies.joinToString("\n") { hobby ->
            "${hobby.category}으로는 ${hobby.items.joinToString(", ")} 등을 즐깁니다."
        }
        return ResumeChunk(
            id = ChunkIdGenerator.forHobbies(),
            type = "hobby",
            content = content,
            source = objectMapper.convertValue(mapOf("items" to resume.hobbies))
        )
    }

    private fun createInterestsChunk(resume: Resume): ResumeChunk? {
        if (resume.interests.isEmpty()) return null
        val content = "최근 주요 관심사는 ${resume.interests.joinToString(", ")} 등 입니다."
        return ResumeChunk(
            id = ChunkIdGenerator.forInterests(),
            type = "interest",
            content = content,
            source = objectMapper.convertValue(mapOf("items" to resume.interests))
        )
    }

    private fun createMbtiChunk(resume: Resume): ResumeChunk? {
        if (resume.mbti.isBlank()) return null
        return ResumeChunk(
            id = ChunkIdGenerator.forMbti(),
            type = "personality",
            content = "저의 MBTI는 ${resume.mbti}입니다.",
            source = objectMapper.convertValue(mapOf("mbti" to resume.mbti))
        )
    }

    private fun createExperienceChunks(resume: Resume): List<ResumeChunk> {
        return resume.experiences.map { exp ->
            val content = """
                ${exp.company}에서 근무한 경력 정보입니다.
                근무 기간은 ${exp.period.start}부터 ${exp.period.end}까지이며, ${exp.position}으로 근무했습니다.
            """.trimIndent()
            ResumeChunk(
                id = ChunkIdGenerator.forExperience(exp.company),
                type = "experience",
                content = content,
                company = exp.company,
                source = objectMapper.convertValue(exp)
            )
        }
    }

    private fun createProjectChunks(resume: Resume): List<ResumeChunk> {
        return resume.projects.map { proj ->
            val content = """
                프로젝트 '${proj.title}'에 대한 상세 정보입니다.
                - 소속: ${proj.company}
                - 기간: ${proj.period.start} ~ ${proj.period.end}
                - 설명: ${proj.description}
                - 주요 기술: ${proj.skills.joinToString(", ")}
            """.trimIndent()
            ResumeChunk(
                id = ChunkIdGenerator.forProject(proj.title),
                type = "project",
                content = content,
                company = proj.company,
                skills = proj.skills,
                source = objectMapper.convertValue(proj)
            )
        }
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/service/ResumeDataProvider.kt`
```kotlin
package com.dd3ok.whoamai.application.service

import com.dd3ok.whoamai.application.port.out.LoadResumePort
import com.dd3ok.whoamai.application.port.out.ResumeProviderPort
import com.dd3ok.whoamai.domain.Resume
import jakarta.annotation.PostConstruct
import org.springframework.stereotype.Component

@Component
class ResumeDataProvider(
    private val loadResumePort: LoadResumePort
) : ResumeProviderPort {

    private lateinit var resume: Resume

    @PostConstruct
    fun initialize() {
        this.resume = loadResumePort.load()
    }

    override fun getResume(): Resume {
        if (!isInitialized()) {
            throw IllegalStateException("Resume data is not initialized yet.")
        }
        return this.resume
    }

    override fun isInitialized(): Boolean = ::resume.isInitialized && resume.name.isNotBlank()
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/service/dto/QueryType.kt`
```kotlin
package com.dd3ok.whoamai.application.service.dto

enum class QueryType {
    NON_RAG,   // 일반 대화 (이전 CHIT_CHAT + GENERAL_CONVERSATION)
    RESUME_RAG // 이력서 정보 질문
}
```

### `src/main/kotlin/com/dd3ok/whoamai/application/service/dto/RouteDecision.kt`
```kotlin
package com.dd3ok.whoamai.application.service.dto

data class RouteDecision(
    val queryType: QueryType,
    val company: String? = null,
    val skills: List<String>? = null,
    val keywords: List<String>? = null
)
```

### `src/main/kotlin/com/dd3ok/whoamai/common/config/CorsConfig.kt`
```kotlin
package com.dd3ok.whoamai.common.config

import org.springframework.context.annotation.Configuration
import org.springframework.web.reactive.config.CorsRegistry
import org.springframework.web.reactive.config.EnableWebFlux
import org.springframework.web.reactive.config.WebFluxConfigurer

@Configuration
@EnableWebFlux
class CorsConfig : WebFluxConfigurer {

    override fun addCorsMappings(registry: CorsRegistry) {
        registry.addMapping("/api/**") // API 경로에 대해서만 CORS 적용
            .allowedOrigins("https://dd3ok.github.io", "http://localhost:3000") // GitHub Pages와 로컬 개발용 프론트엔드 주소 허용
            .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS") // 허용할 HTTP 메소드
            .allowedHeaders("*") // 모든 헤더 허용
            .allowCredentials(true) // Credential 허용
            .maxAge(3600) // pre-flight 요청 캐시 시간 (초)
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/common/config/GeminiConfig.kt`
```kotlin
package com.dd3ok.whoamai.common.config

import com.google.genai.Client
import com.google.genai.types.Content
import com.google.genai.types.GenerateContentConfig
import com.google.genai.types.Part
import org.springframework.beans.factory.annotation.Qualifier
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
class GeminiConfig(
    @Value("\${gemini.api.key}") private val apiKey: String,
    private val modelProperties: GeminiModelProperties,
    private val promptProperties: PromptProperties
) {

    @Bean
    fun geminiClient(): Client {
        return Client.builder()
            .apiKey(apiKey)
            .build()
    }

    @Bean
    @Qualifier("generationConfig")
    fun generationConfig(): GenerateContentConfig {
        return GenerateContentConfig.builder()
            .maxOutputTokens(modelProperties.maxOutputTokens)
            .temperature(modelProperties.temperature)
            .systemInstruction(Content.fromParts(Part.fromText(promptProperties.systemInstruction)))
            .build()
    }

    @Bean
    @Qualifier("routingConfig")
    fun routingConfig(): GenerateContentConfig {
        return GenerateContentConfig.builder()
            // 라우팅은 간단한 JSON만 필요하므로 토큰 제한을 낮춰 비용 절감
            .maxOutputTokens(512)
            // 일관된 JSON 출력을 위해 온도를 낮춤
            .temperature(0.1f)
            .systemInstruction(Content.fromParts(Part.fromText(promptProperties.routingInstruction)))
            .build()
    }

    @Bean
    @Qualifier("summarizationConfig")
    fun summarizationConfig(): GenerateContentConfig {
        return GenerateContentConfig.builder()
            .maxOutputTokens(1024)
            .temperature(0.5f)
            // 요약 작업은 별도 시스템 지침이 필요 없을 수 있음 (필요 시 추가)
            .build()
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/common/config/PromptProperties.kt`
```kotlin
package com.dd3ok.whoamai.common.config

import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.context.annotation.Configuration

@Configuration
@ConfigurationProperties(prefix = "prompts")
data class PromptProperties(
    var systemInstruction: String = "",
    var routingInstruction: String = "",
    var routingTemplate: String = "",
    var ragTemplate: String = "",
    var conversationalTemplate: String = ""
)

@Configuration
@ConfigurationProperties(prefix = "gemini.model")
data class GeminiModelProperties(
    var name: String = "",
    var text: String = "",
    var temperature: Float = 0.7f,
    var maxOutputTokens: Int = 8192
)
```

### `src/main/kotlin/com/dd3ok/whoamai/common/config/WebSocketConfig.kt`
```kotlin
package com.dd3ok.whoamai.common.config

import com.dd3ok.whoamai.adapter.`in`.web.StreamChatWebSocketHandler
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.web.reactive.HandlerMapping
import org.springframework.web.reactive.handler.SimpleUrlHandlerMapping

@Configuration
class WebSocketConfig {

    @Bean
    fun webSocketHandlerMapping(streamChatWebSocketHandler: StreamChatWebSocketHandler): HandlerMapping {
        val map = mapOf("/ws/chat" to streamChatWebSocketHandler)
        return SimpleUrlHandlerMapping(map).apply { order = 1 }
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/common/util/ChunkIdGenerator.kt`
```kotlin
package com.dd3ok.whoamai.common.util

/**
 * 이력서 데이터 조각(Chunk)의 ID 생성 규칙을 관리하는 유틸리티.
 */
object ChunkIdGenerator {
    private val sanitizeRegex = Regex("[^a-zA-Z0-9ㄱ-ㅎㅏ-ㅣ가-힣]+")

    private fun sanitize(input: String): String {
        return input.replace(sanitizeRegex, "_").trim('_')
    }

    fun forProject(title: String): String = "project_${sanitize(title)}"
    fun forExperience(company: String): String = "experience_${sanitize(company)}"
    fun forSummary(): String = "summary"
    fun forTotalExperience(): String = "experience_total_summary"
    fun forSkills(): String = "skills"
    fun forEducation(): String = "education"
    fun forCertificates(): String = "certificates"
    fun forInterests(): String = "interests"
    fun forMbti(): String = "mbti"
    fun forHobbies(): String = "hobbies"
}
```

### `src/main/kotlin/com/dd3ok/whoamai/domain/ChatHistory.kt`
```kotlin
package com.dd3ok.whoamai.domain

class ChatHistory(
    val userId: String,
    messages: List<ChatMessage> = emptyList()
) {
    private val _history: MutableList<ChatMessage> = messages.toMutableList()

    val history: List<ChatMessage> get() = _history.toList()

    fun addMessage(msg: ChatMessage) {
        _history.add(msg)
    }
}
```

### `src/main/kotlin/com/dd3ok/whoamai/domain/ChatMessage.kt`
```kotlin
package com.dd3ok.whoamai.domain

data class ChatMessage(
    val role: String,
    val text: String
)
```

### `src/main/kotlin/com/dd3ok/whoamai/domain/MessageType.kt`
```kotlin
package com.dd3ok.whoamai.domain

enum class MessageType {
    USER, AI, SYSTEM, ERROR
}
```

### `src/main/kotlin/com/dd3ok/whoamai/domain/ResumeSection.kt`
```kotlin
package com.dd3ok.whoamai.domain

import com.fasterxml.jackson.annotation.JsonIgnoreProperties

@JsonIgnoreProperties(ignoreUnknown = true)
data class Resume(
    val name: String = "",
    val mbti: String = "",
    val summary: String = "",
    val blog: String = "",
    val skills: List<String> = emptyList(),
    val certificates: List<Certificate> = emptyList(),
    val education: List<Education> = emptyList(),
    val experiences: List<Experience> = emptyList(),
    val projects: List<Project> = emptyList(),
    val hobbies: List<Hobby> = emptyList(),
    val interests: List<String> = emptyList()
)
@JsonIgnoreProperties(ignoreUnknown = true)
data class Certificate(val title: String = "", val issuedAt: String = "", val issuer: String = "")
@JsonIgnoreProperties(ignoreUnknown = true)
data class Education(val school: String = "", val major: String = "", val period: Period = Period(), val degree: String = "")
@JsonIgnoreProperties(ignoreUnknown = true)
data class Experience(val company: String = "", val aliases: List<String> = emptyList(), val period: Period = Period(), val position: String = "", val tags: List<String> = emptyList())
@JsonIgnoreProperties(ignoreUnknown = true)
data class Project(val title: String = "", val company: String = "", val period: Period = Period(), val skills: List<String> = emptyList(), val tags: List<String> = emptyList(), val description: String = "")
@JsonIgnoreProperties(ignoreUnknown = true)
data class Period(val start: String = "", val end: String = "")
@JsonIgnoreProperties(ignoreUnknown = true)
data class Hobby(val category: String = "", val items: List<String> = emptyList())

```

### `src/main/kotlin/com/dd3ok/whoamai/domain/StreamMessage.kt`
```kotlin
package com.dd3ok.whoamai.domain

import com.fasterxml.jackson.annotation.JsonCreator
import com.fasterxml.jackson.annotation.JsonProperty

data class StreamMessage @JsonCreator constructor(
    @param:JsonProperty("uuid") val uuid: String,
    @param:JsonProperty("type") val type: MessageType,
    @param:JsonProperty("content") val content: String,
)

```

### `src/test/kotlin/com/dd3ok/whoamai/WhoAmAiApplicationTests.kt`
```kotlin
package com.dd3ok.whoamai

import org.junit.jupiter.api.Test

// @SpringBootTest
class WhoAmAiApplicationTests {

    @Test
    fun contextLoads() {
    }

}

```

