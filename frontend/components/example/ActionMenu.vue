<template>
  <action-menu
    :items="items"
    :text="$t('dataset.actions')"
    @create="$emit('create')"
    @upload="$emit('upload')"
    @download="$emit('download')"
    @assign="$emit('assign')"
    @reset="$emit('reset')"
  />
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiAccountCheck, mdiUpload, mdiDownload, mdiUpdate } from '@mdi/js'
import ActionMenu from '~/components/utils/ActionMenu.vue'

export default Vue.extend({
  components: {
    ActionMenu
  },

  computed: {
    items() {
      return [
        {
          title: this.$t('dataset.importDataset'),
          icon: mdiUpload,
          event: 'upload'
        },
        {
          title: this.$t('dataset.exportDataset'),
          icon: mdiDownload,
          event: 'download'
        },
        {
          title: this.$t('dataset.assignToMember'),
          icon: mdiAccountCheck,
          event: 'assign'
        },
        {
          title: this.$t('dataset.resetAssignment'),
          icon: mdiUpdate,
          event: 'reset'
        }
      ]
    }
  }
})
</script>
