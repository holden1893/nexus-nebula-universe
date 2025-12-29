export type Listing = {
  id: string;
  title: string;
  description: string | null;
  price_cents: number;
  currency: string;
  tags: string[] | null;
  seller: string | null;
  image_url: string | null;
  is_published: boolean;
  created_at: string;
  updated_at: string;
};
