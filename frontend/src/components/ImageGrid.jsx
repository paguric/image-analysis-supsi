import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';

export default function ImageGrid({ items }) {
  return (
    <ImageList sx={{ width: '100%', height: '100%' }} cols={2} rowHeight="auto">
      {items.map((item) => (
        <ImageListItem key={item.img}>
          <img
            srcSet={item.img}
            src={item.img}
            alt={item.title}
            loading="lazy"
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          />
        </ImageListItem>
      ))}
    </ImageList>
  );
}
