export class AttachmentItem {
  constructor(
    public id: number,
    public file: string,
    public filename: string,
    public projectId: number
  ) {}

  static valueOf(item: any): AttachmentItem {
    return new AttachmentItem(item.id, item.file, item.filename, item.project)
  }
}
