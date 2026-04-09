import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import ImageListItemBar from '@mui/material/ImageListItemBar';

export default function ImageGrid({ items, title }) {
  return (
    <div className="flex flex-col w-full h-full">
      {title && (
        <p className="text-sm font-semibold text-center w-full mb-1 shrink-0">{title}</p>
      )}
      <ImageList sx={{ width: '100%', height: '100%' }} cols={2} rowHeight="auto">
        {items.map((item, i) => (
          <ImageListItem key={item.img}>
            <img
              srcSet={item.img}
              src={item.img}
              alt={item.title}
              loading="lazy"
              style={{ width: '100%', height: '100%', objectFit: 'contain' }}
            />
            <ImageListItemBar
              title={i + 1}
              position="top"
              sx={{
                background: 'transparent',
                '& .MuiImageListItemBar-title': {
                  fontSize: '0.8rem',
                  fontWeight: 'bold',
                  color: 'yellow'
                }
              }}
            />
          </ImageListItem>
        ))}
      </ImageList>
    </div>
  );
}