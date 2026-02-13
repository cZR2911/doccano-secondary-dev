import { AttachmentItem } from './attachment'
import ApiService from '@/services/api.service'

export class AttachmentRepository {
  constructor(private readonly request = ApiService) {}

  async list(projectId: string): Promise<AttachmentItem[]> {
    const url = `/projects/${projectId}/attachments`
    const response = await this.request.get(url)
    return response.data.map((item: any) => AttachmentItem.valueOf(item))
  }

  async create(projectId: string, file: File): Promise<AttachmentItem> {
    const url = `/projects/${projectId}/attachments`
    const formData = new FormData()
    formData.append('file', file)
    const response = await this.request.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return AttachmentItem.valueOf(response.data)
  }

  async delete(projectId: string, attachmentId: number): Promise<void> {
    const url = `/projects/${projectId}/attachments/${attachmentId}`
    await this.request.delete(url)
  }
}
