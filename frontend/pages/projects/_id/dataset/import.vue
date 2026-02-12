<template>
  <v-card>
    <v-card-title>
      {{ $t('dataset.importDataTitle') }}
    </v-card-title>
    <v-card-text>
      <v-overlay :value="isImporting">
        <v-progress-circular indeterminate size="64" />
      </v-overlay>
      <v-select
        v-model="selected"
        :items="catalog"
        item-text="displayName"
        :menu-props="{ maxHeight: 600 }"
        :label="$t('dataset.fileFormat')"
        outlined
      />
      <v-form v-model="valid">
        <template v-for="(item, key) in textFields">
          <v-combobox
            v-if="['column_data', 'column_label'].includes(key)"
            :key="key"
            v-model="option[key]"
            :items="columns"
            :label="$te('dataset.' + key) ? $t('dataset.' + key) : item.title"
            :hint="
              $te('dataset.' + key + '_hint')
                ? $t('dataset.' + key + '_hint')
                : item.description
            "
            persistent-hint
            :rules="requiredRules"
            multiple
            chips
            small-chips
            deletable-chips
            outlined
            :append-outer-icon="mdiSelectAll"
            @click:append-outer="selectAll(key)"
          />
          <v-text-field
            v-else
            :key="key"
            v-model="option[key]"
            :label="$te('dataset.' + key) ? $t('dataset.' + key) : item.title"
            :hint="
              $te('dataset.' + key + '_hint')
                ? $t('dataset.' + key + '_hint')
                : item.description
            "
            persistent-hint
            :rules="requiredRules"
            outlined
          />
        </template>
        <v-select
          v-for="(val, key) in selectFields"
          :key="key"
          v-model="option[key]"
          :items="val.enum"
          :label="$te('dataset.' + key) ? $t('dataset.' + key) : val.title"
          outlined
        >
          <template #selection="{ item }">
            {{ toVisualize(item) }}
          </template>
          <template #item="{ item }">
            {{ toVisualize(item) }}
          </template>
        </v-select>
      </v-form>
      <v-sheet
        v-if="selected"
        :dark="!$vuetify.theme.dark"
        :light="$vuetify.theme.dark"
        class="mb-5 pa-5"
      >
        <pre>{{ example }}</pre>
      </v-sheet>
      <div v-if="selected === 'JSONL(Relation)'">
        <p class="body-1">{{ $t('dataset.importDataMessage') }}</p>
        <v-sheet :dark="!$vuetify.theme.dark" :light="$vuetify.theme.dark" class="mb-5 pa-5">
          <pre>{{ JSON.stringify(JSON.parse(example.replaceAll("'", '"')), null, 4) }}</pre>
        </v-sheet>
      </div>
      <file-pond
        v-if="selected && acceptedFileTypes !== '*'"
        ref="pond"
        chunk-uploads="true"
        :label-idle="$t('dataset.dropFiles')"
        :allow-multiple="true"
        :accepted-file-types="acceptedFileTypes"
        :server="server"
        :files="myFiles"
        @processfile="handleFilePondProcessFile"
        @removefile="handleFilePondRemoveFile"
      />
      <file-pond
        v-if="selected && acceptedFileTypes === '*'"
        ref="pond"
        chunk-uploads="true"
        :label-idle="$t('dataset.dropFiles')"
        :allow-multiple="true"
        :server="server"
        :files="myFiles"
        @processfile="handleFilePondProcessFile"
        @removefile="handleFilePondRemoveFile"
      />
      <v-data-table
        v-if="errors.length > 0"
        :headers="headers"
        :items="errors"
        class="elevation-1"
      ></v-data-table>
    </v-card-text>
    <v-card-actions>
      <v-btn class="text-capitalize ms-2 primary" :disabled="isDisabled" @click="importDataset">
        {{ $t('generic.import') }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type'
import 'filepond/dist/filepond.min.css'
import Cookies from 'js-cookie'
import vueFilePond from 'vue-filepond'
import { mdiSelectAll } from '@mdi/js'
const FilePond = vueFilePond(FilePondPluginFileValidateType)

export default {
  components: {
    FilePond
  },

  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject', 'isProjectAdmin'],

  validate({ params }) {
    return /^\d+$/.test(params.id)
  },

  data() {
    return {
      catalog: [],
      selected: null,
      myFiles: [],
      columns: [],
      option: { column_data: [], column_label: [], delimiter: '' },
      taskId: null,
      polling: null,
      errors: [],
      mdiSelectAll,
      headers: [
        { text: this.$t('dataset.filename'), value: 'filename' },
        { text: this.$t('dataset.line'), value: 'line' },
        { text: this.$t('dataset.message'), value: 'message' }
      ],
      requiredRules: [(v) => !!v || this.$t('dataset.fieldRequired')],
      server: {
        url: '/v1/fp',
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken')
        },
        process: {
          url: '/process/',
          method: 'POST'
        },
        patch: '/patch/',
        revert: '/revert/',
        restore: '/restore/',
        load: '/load/',
        fetch: '/fetch/'
      },
      uploadedFiles: [],
      valid: false,
      isImporting: false
    }
  },

  computed: {
    isDisabled() {
      return this.uploadedFiles.length === 0 || this.taskId !== null || !this.valid
    },
    properties() {
      const item = this.catalog.find((item) => item.displayName === this.selected)
      if (item) {
        return item.properties
      } else {
        return {}
      }
    },
    textFields() {
      const asArray = Object.entries(this.properties)
      const textFields = asArray.filter(([_, value]) => !('enum' in value))
      return Object.fromEntries(textFields)
    },
    selectFields() {
      const asArray = Object.entries(this.properties)
      const textFields = asArray.filter(([_, value]) => 'enum' in value)
      return Object.fromEntries(textFields)
    },
    acceptedFileTypes() {
      const item = this.catalog.find((item) => item.displayName === this.selected)
      if (item) {
        return item.acceptTypes
      } else {
        return ''
      }
    },
    example() {
      const item = this.catalog.find((item) => item.displayName === this.selected)
      if (item) {
        const column_data = 'column_data'
        const column_label = 'column_label'
        if (column_data in this.option && column_label in this.option) {
          let cData = this.option[column_data]
          let cLabel = this.option[column_label]
          if (Array.isArray(cData)) cData = cData.join(',')
          if (Array.isArray(cLabel)) cLabel = cLabel.join(',')

          return item.example
            .replaceAll(column_data, cData)
            .replaceAll(column_label, cLabel)
            .trim()
        } else {
          return item.example.trim()
        }
      } else {
        return ''
      }
    }
  },

  watch: {
    selected() {
      const item = this.catalog.find((item) => item.displayName === this.selected)
      for (const [key, value] of Object.entries(item.properties)) {
        if (['column_data', 'column_label'].includes(key)) {
          this.option[key] = value.default ? [value.default] : []
        } else {
          this.option[key] = value.default
        }
      }
      this.myFiles = []
      for (const file of this.uploadedFiles) {
        this.$repositories.parse.revert(file.serverId)
      }
      this.uploadedFiles = []
      this.errors = []
    }
  },

  async created() {
    this.catalog = await this.$repositories.catalog.list(this.$route.params.id)
    this.pollData()
  },

  beforeDestroy() {
    clearInterval(this.polling)
  },

  methods: {
    handleFilePondProcessFile(error, file) {
      console.log(error)
      if (!error) {
        this.fetchColumns(file.serverId)
      }
      this.uploadedFiles.push(file)
      this.$nextTick()
    },
    async fetchColumns(uploadId) {
      try {
        const { columns } = await this.$repositories.parse.getColumns(
          this.$route.params.id,
          uploadId
        )
        this.columns = columns
        // Automatically remove non-existent default columns (text/label)
        for (const key in this.option) {
          if (Array.isArray(this.option[key])) {
            this.option[key] = this.option[key].filter((col) => columns.includes(col))
            if (this.option[key].length === 0) {
              if (key === 'column_label') {
                const aliases = [
                  'label',
                  'tag',
                  'category',
                  'class',
                  'target',
                  'sentiment',
                  'emotion',
                  'topic',
                  'intent',
                  '标签',
                  '类别',
                  '分类',
                  '目标'
                ]
                // 1. Exact match
                let match = columns.find((col) =>
                  aliases.some((alias) => col.toLowerCase() === alias.toLowerCase())
                )
                // 2. Partial match
                if (!match) {
                  match = columns.find((col) =>
                    aliases.some((alias) => col.toLowerCase().includes(alias.toLowerCase()))
                  )
                }
                if (match) this.option[key] = [match]
              } else if (key === 'column_data') {
                const aliases = [
                  'text',
                  'data',
                  'body',
                  'content',
                  'sentence',
                  'document',
                  'input',
                  'prompt',
                  'query',
                  'question',
                  'answer',
                  'response',
                  'instruction',
                  'summary',
                  'review',
                  'comment',
                  'utterance',
                  '文本',
                  '内容',
                  '句子',
                  '评论',
                  '输入'
                ]
                // 1. Exact match
                let match = columns.find((col) =>
                  aliases.some((alias) => col.toLowerCase() === alias.toLowerCase())
                )
                // 2. Partial match
                if (!match) {
                  match = columns.find((col) =>
                    aliases.some((alias) => col.toLowerCase().includes(alias.toLowerCase()))
                  )
                }
                if (match) this.option[key] = [match]
              }
            }
          }
        }
        // Force Strategy (Simple & Crude)
        // If text column is missing, pick the 1st one
        if (
          'column_data' in this.option &&
          (!this.option.column_data || this.option.column_data.length === 0) &&
          columns.length > 0
        ) {
          this.option.column_data = [columns[0]]
        }

        // If label column is missing, pick the last available one
        if (
          'column_label' in this.option &&
          (!this.option.column_label || this.option.column_label.length === 0) &&
          columns.length > 0
        ) {
          // Get currently selected text column (might have just been set)
          const textCols = this.option.column_data || []
          const textCol = textCols.length > 0 ? textCols[0] : null

          // Find candidates (exclude text column)
          const candidates = columns.filter((col) => col !== textCol)

          if (candidates.length > 0) {
            // Pick the last one
            this.option.column_label = [candidates[candidates.length - 1]]
          }
        }
      } catch (e) {
        console.error(e)
      }
    },
    handleFilePondRemoveFile(error, file) {
      console.log(error)
      const index = this.uploadedFiles.findIndex((item) => item.id === file.id)
      if (index > -1) {
        this.uploadedFiles.splice(index, 1)
        this.$nextTick()
      }
    },
    async importDataset() {
      this.isImporting = true
      const item = this.catalog.find((item) => item.displayName === this.selected)
      const options = { ...this.option }
      for (const key in options) {
        if (Array.isArray(options[key])) {
          options[key] = options[key].join(',')
        }
      }
      this.taskId = await this.$repositories.parse.analyze(
        this.$route.params.id,
        item.name,
        item.taskId,
        this.uploadedFiles.map((item) => item.serverId),
        options
      )
    },
    pollData() {
      this.polling = setInterval(async () => {
        if (this.taskId) {
          const res = await this.$repositories.taskStatus.get(this.taskId)
          if (res.ready) {
            this.taskId = null
            this.errors = res.result.error
            this.myFiles = []
            this.uploadedFiles = []
            this.isImporting = false
            if (this.errors.length === 0) {
              this.$router.push(`/projects/${this.$route.params.id}/dataset`)
            }
          }
        }
      }, 3000)
    },
    toVisualize(text) {
      if (text === '\t') {
        return 'Tab'
      } else if (text === ' ') {
        return 'Space'
      } else if (text === '') {
        return 'None'
      } else {
        return text
      }
    },
    selectAll(key) {
      if (this.option[key].length === this.columns.length) {
        this.option[key] = []
      } else {
        this.option[key] = [...this.columns]
      }
    }
  }
}
</script>
