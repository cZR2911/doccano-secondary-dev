<template>
  <div>
    <h2>搜索按钮测试页面</h2>
    <p>这个页面用于测试搜索按钮组件是否能正常显示</p>
    
    <div class="test-section">
      <h3>1. 直接使用搜索按钮组件</h3>
      <button-search @click:search="handleSearchClick" />
      
      <h3>2. 检查翻译是否生效</h3>
      <p>搜索提示文本: {{ $t('annotation.searchTooltip') }}</p>
      <p>搜索弹窗标题: {{ $t('annotation.searchPopupTitle') }}</p>
      
      <h3>3. 检查其他按钮的汉化状态</h3>
      <p>过滤提示: {{ $t('annotation.selectFilterTooltip') }}</p>
      <p>已选提示: {{ $t('annotation.checkedTooltip') }}</p>
      <p>未选提示: {{ $t('annotation.notCheckedTooltip') }}</p>
    </div>
    
    <div v-if="showSearchDialog" class="dialog-overlay">
      <div class="dialog-content">
        <h3>搜索对话框测试</h3>
        <p>搜索功能测试中...</p>
        <v-btn @click="showSearchDialog = false">关闭</v-btn>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import ButtonSearch from '@/components/tasks/toolbar/buttons/ButtonSearch.vue'

export default Vue.extend({
  components: {
    ButtonSearch
  },

  data() {
    return {
      showSearchDialog: false
    }
  },

  methods: {
    handleSearchClick() {
      console.log('搜索按钮被点击了！')
      this.showSearchDialog = true
    }
  }
})
</script>

<style scoped>
.test-section {
  margin: 20px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-content {
  background: white;
  padding: 20px;
  border-radius: 4px;
  max-width: 500px;
  width: 90%;
}
</style>