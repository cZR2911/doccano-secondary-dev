import { AttachmentRepository } from '~/domain/models/attachment/attachmentRepository'
import { AttachmentItem } from '~/domain/models/attachment/attachment'

export class AttachmentApplicationService {
  constructor(private readonly repository: AttachmentRepository) {}

  public async list(projectId: string): Promise<AttachmentItem[]> {
    return await this.repository.list(projectId)
  }

  public async create(projectId: string, file: File): Promise<AttachmentItem> {
    return await this.repository.create(projectId, file)
  }

  public async delete(projectId: string, attachmentId: number): Promise<void> {
    await this.repository.delete(projectId, attachmentId)
  }
}
