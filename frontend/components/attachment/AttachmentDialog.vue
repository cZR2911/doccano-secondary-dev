<template>
  <v-dialog v-model="dialog" max-width="800px">
    <template #activator="{ on, attrs }">
      <v-btn
        icon
        v-bind="attrs"
        :title="$t('dataset.attachments')"
        v-on="on"
      >
        <v-icon>{{ mdiPaperclip }}</v-icon>
      </v-btn>
    </template>
    <attachment-list />
  </v-dialog>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiPaperclip } from '@mdi/js'
import AttachmentList from './AttachmentList.vue'

export default Vue.extend({
  components: { AttachmentList },
  data() {
    return {
      dialog: false
    }
  },
  computed: {
    mdiPaperclip() {
      return mdiPaperclip
    }
  }
})
</script>
