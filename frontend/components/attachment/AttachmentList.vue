<template>
  <v-card>
    <v-card-title>
      {{ customTitle || $t('dataset.attachments') }}
      <v-spacer />
      <input
        ref="fileInput"
        type="file"
        style="display: none"
        multiple
        @change="uploadFiles"
      />
    </v-card-title>

    <div
      v-if="isProjectAdmin"
      class="drop-zone mb-3 mx-4 pa-5 text-center"
      :class="{ 'drop-zone-active': isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="fileInput.click()"
    >
      <v-icon large color="grey darken-1">
        {{ mdiCloudUpload }}
      </v-icon>
      <div class="mt-2 grey--text text--darken-1">
        {{ $t('dataset.dropFiles') }}
      </div>
    </div>

    <v-data-table
      :headers="headers"
      :items="attachments"
      :loading="loading"
    >
      <template #[`item.file`]="{ item }">
        <a :href="item.file" target="_blank">{{ item.filename }}</a>
      </template>
      <template #[`item.actions`]="{ item }">
        <v-icon
          v-if="isProjectAdmin"
          small
          @click="deleteAttachment(item)"
        >
          {{ mdiDelete }}
        </v-icon>
      </template>
    </v-data-table>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiDelete, mdiCloudUpload } from '@mdi/js'
import { AttachmentApplicationService } from '~/services/application/attachment/attachmentApplicationService'
import { AttachmentRepository } from '~/domain/models/attachment/attachmentRepository'
import { AttachmentItem } from '~/domain/models/attachment/attachment'

export default Vue.extend({
  props: {
    customTitle: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      attachments: [] as AttachmentItem[],
      loading: false,
      uploading: false,
      isDragging: false,
      isProjectAdmin: false,
      service: new AttachmentApplicationService(new AttachmentRepository())
    }
  },
  computed: {
    projectId(): string {
      return this.$route.params.id
    },
    fileInput(): HTMLElement {
      return this.$refs.fileInput as HTMLElement
    },
    headers(): any[] {
      return [
        { text: this.$t('dataset.filename'), value: 'file' },
        { text: this.$t('dataset.actions'), value: 'actions', sortable: false }
      ]
    },
    mdiDelete() {
      return mdiDelete
    },
    mdiCloudUpload() {
      return mdiCloudUpload
    }
  },
  async mounted() {
    const member = await this.$repositories.member.fetchMyRole(this.projectId)
    this.isProjectAdmin = member.isProjectAdmin
    await this.fetchAttachments()
  },
  methods: {
    async fetchAttachments() {
      this.loading = true
      try {
        this.attachments = await this.service.list(this.projectId)
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    async handleDrop(event: DragEvent) {
      this.isDragging = false
      const files = event.dataTransfer?.files
      if (files && files.length > 0) {
        await this.processFiles(files)
      }
    },
    async uploadFiles(event: Event) {
      const input = event.target as HTMLInputElement
      if (!input.files || input.files.length === 0) return
      await this.processFiles(input.files)
      // Reset input to allow selecting the same file again
      input.value = ''
    },
    async processFiles(files: FileList) {
      this.uploading = true
      try {
        await Promise.all(
          Array.from(files).map((file) => this.service.create(this.projectId, file))
        )
        await this.fetchAttachments()
      } catch (e) {
        console.error(e)
      } finally {
        this.uploading = false
      }
    },
    async deleteAttachment(item: AttachmentItem) {
      if (!confirm('Are you sure you want to delete this attachment?')) return
      try {
        await this.service.delete(this.projectId, item.id)
        await this.fetchAttachments()
      } catch (e) {
        console.error(e)
      }
    }
  }
})
</script>

<style scoped>
.drop-zone {
  border: 2px dashed #ccc;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: #fafafa;
}

.theme--dark .drop-zone {
  background-color: #1e1e1e;
  border-color: #444;
}

.drop-zone:hover,
.drop-zone-active {
  border-color: #1976d2;
  background-color: #e3f2fd;
}

.theme--dark .drop-zone:hover,
.theme--dark .drop-zone-active {
  border-color: #2196f3;
  background-color: #0d47a1;
}
</style>
