<template>
  <v-sheet
    height="200"
    class="d-flex flex-column align-center justify-center pa-0 grey lighten-4 task-preview
      overflow-hidden"
    style="
      cursor: pointer;
      position: relative;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
    "
    @click="$emit('click')"
  >
    <!-- 模拟窗口标题栏 -->
    <div class="preview-header w-100 px-3 py-1 d-flex align-center white border-bottom">
      <div class="d-flex mr-2">
        <div class="circle red mr-1" />
        <div class="circle yellow mr-1" />
        <div class="circle green" />
      </div>
      <div class="grey--text text-caption ml-2">Doccano 预览</div>
    </div>

    <!-- 内容区域 -->
    <div
      class="preview-content w-100 flex-grow-1 d-flex align-center justify-center pa-3 white
        relative"
    >
      
      <!-- 1. 文本分类 (Document Classification) -->
      <div v-if="type === 'DocumentClassification'" class="text-center w-100">
        <v-card outlined class="mb-3 pa-2 text-left body-2 grey lighten-5">
          "这部电影的特效简直炸裂！剧情也全程高能，五星推荐！"
        </v-card>
        <div class="d-flex justify-center">
          <v-chip color="success" class="mr-2 elevation-2" small>
            <v-icon left x-small>mdi-thumb-up</v-icon>
            正面
          </v-chip>
          <v-chip color="grey lighten-3" class="grey--text" small>
            <v-icon left x-small>mdi-thumb-down</v-icon>
            负面
          </v-chip>
        </div>
      </div>

      <!-- 2. 序列标注 (Sequence Labeling) -->
      <div v-else-if="type === 'SequenceLabeling'" class="text-left w-100 px-2">
        <div class="text-body-2 black--text" style="line-height: 2.5;">
          <div class="d-inline-block text-center mr-1">
            <span class="blue lighten-4 px-1 rounded">马云</span>
            <div
              class="blue--text font-weight-bold"
              style="font-size: 10px; line-height: 1;"
            >
              人名
            </div>
          </div>
          在
          <div class="d-inline-block text-center mx-1">
            <span class="green lighten-4 px-1 rounded">杭州</span>
            <div
              class="green--text font-weight-bold"
              style="font-size: 10px; line-height: 1;"
            >
              地点
            </div>
          </div>
          创办了
          <div class="d-inline-block text-center ml-1">
            <span class="orange lighten-4 px-1 rounded">阿里巴巴</span>
            <div
              class="orange--text font-weight-bold"
              style="font-size: 10px; line-height: 1;"
            >
              公司
            </div>
          </div>
        </div>
      </div>

      <!-- 3. 序列到序列 (Seq2seq) -->
      <div v-else-if="type === 'Seq2seq'" class="w-100 px-2">
        <div class="d-flex align-center justify-space-between">
          <v-card
            outlined
            class="pa-2 flex-grow-1 grey lighten-5 caption mb-0 mr-1"
            height="60"
          >
            <div class="grey--text text--darken-1 mb-1">输入 (英文)</div>
            <div class="font-weight-medium">Hello World</div>
          </v-card>
          <v-icon color="primary" class="mx-1">mdi-arrow-right-bold</v-icon>
          <v-card
            outlined
            class="pa-2 flex-grow-1 blue lighten-5 caption mb-0 ml-1"
            height="60"
            style="border-color: #bbdefb;"
          >
            <div class="blue--text text--darken-2 mb-1">输出 (中文)</div>
            <div class="font-weight-medium">你好，世界</div>
          </v-card>
        </div>
      </div>

      <!-- 4. 意图识别 (Intent Detection) -->
      <div v-else-if="type === 'IntentDetectionAndSlotFilling'" class="text-left w-100">
        <!-- 意图标签 -->
        <div class="mb-4 text-center">
          <span class="grey--text caption mr-2">识别意图:</span>
          <v-chip color="purple" dark x-small label class="px-2 py-1">
            <v-icon left x-small>mdi-ticket</v-icon>
            订票
          </v-chip>
        </div>
        <!-- 槽位填充 -->
        <div class="text-center body-2">
          "帮我订一张
          <span
            class="orange lighten-4 px-1 rounded font-weight-medium"
            style="border-bottom: 2px solid orange;"
          >
            明天
          </span>
          去
          <span
            class="green lighten-4 px-1 rounded font-weight-medium"
            style="border-bottom: 2px solid green;"
          >
            北京
          </span>
          的票"
        </div>
        <div class="d-flex justify-center mt-1 caption grey--text">
          <span class="orange--text mr-4">↑ 时间</span>
          <span class="green--text ml-4">↑ 目的地</span>
        </div>
      </div>

      <!-- 5. 知识纠错 (Knowledge Correction) -->
      <div v-else-if="type === 'KnowledgeCorrection'" class="text-left w-100 px-2">
         <div class="text-body-2 black--text text-center">
          <div>原文：人工智<span class="red--text text-decoration-line-through">能</span></div>
          <v-icon small color="grey" class="my-1">mdi-arrow-down</v-icon>
          <div>
            纠错：人工智<span
              class="green--text font-weight-bold"
              style="border: 1px solid green; padding: 0 2px; border-radius: 4px;"
            >
              能
            </span>
          </div>
        </div>
      </div>

      <!-- Fallback -->
      <div v-else class="caption grey--text text-center">
        <v-icon large class="mb-2">mdi-file-document-outline</v-icon>
        <div>{{ type }}</div>
      </div>

    </div>
  </v-sheet>
</template>

<script>
export default {
  name: 'TaskPreview',
  props: {
    type: {
      type: String,
      required: true
    }
  }
}
</script>

<style scoped>
.task-preview {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.task-preview:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
  border-color: #2196F3 !important;
}

.circle {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.red { background-color: #ff5f56; }
.yellow { background-color: #ffbd2e; }
.green { background-color: #27c93f; }

.border-bottom {
  border-bottom: 1px solid #f0f0f0;
}

.w-100 {
  width: 100%;
}
</style>
