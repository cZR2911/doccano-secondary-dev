<template>
  <base-card
    :title="$t('annotation.searchPopupTitle')"
    :cancel-text="$t('generic.close')"
    @cancel="close"
  >
    <template #content>
      <v-text-field
        v-model="searchText"
        :label="$t('generic.searchPlaceholder')"
        outlined
        clearable
        @keyup.enter="performSearch"
      />
      <v-btn
        color="primary"
        class="mt-4"
        @click="performSearch"
      >
        {{ $t('generic.search') }}
      </v-btn>
    </template>
  </base-card>
</template>

<script lang="ts">
import Vue from 'vue'
import BaseCard from '@/components/utils/BaseCard'

export default Vue.extend({
  components: {
    'base-card': BaseCard
  },

  data() {
    return {
      searchText: ''
    }
  },

  methods: {
    performSearch() {
      // 后期实现搜索逻辑
      console.log('搜索:', this.searchText)
    },

    close() {
      this.$emit('click:close')
    }
  }
})
</script>